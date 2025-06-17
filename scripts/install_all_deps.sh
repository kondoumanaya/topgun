#!/opt/homebrew/bin/bash

set -e  # エラー時に停止

# カラー出力設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Installing/updating dependencies with version check...${NC}"

# Bashバージョンチェック
if [[ -z "$BASH_VERSION" ]]; then
    echo -e "${RED}❌ Error: This script requires bash, but you're running with $0${NC}"
    echo "Please run with: /opt/homebrew/bin/bash install_all_deps.sh"
    exit 1
fi

if [[ ${BASH_VERSION%%.*} -lt 4 ]]; then
    echo -e "${RED}❌ Error: This script requires bash 4.0 or later${NC}"
    echo "Current version: $BASH_VERSION"
    echo "Install newer bash: brew install bash"
    exit 1
fi

echo -e "${CYAN}Running with bash version: $BASH_VERSION${NC}"

# conda環境がアクティブか確認
if [[ -z "$CONDA_DEFAULT_ENV" ]] || [[ "$CONDA_DEFAULT_ENV" == "base" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Activating root-bot conda environment...${NC}"
    
    # conda初期化
    if [[ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [[ -f "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh" ]]; then
        source "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh"
    elif command -v conda >/dev/null 2>&1; then
        eval "$(conda shell.bash hook 2>/dev/null || echo '')"
    fi
    
    conda activate root-bot 2>/dev/null || {
        echo -e "${RED}❌ Error: root-bot environment not found. Create it first:${NC}"
        echo "conda create -n root-bot python=3.12 -y"
        exit 1
    }
fi

echo -e "${GREEN}✅ conda environment: $CONDA_DEFAULT_ENV${NC}"

# 記録用配列
FAILED_PACKAGES=()
SUCCESSFUL_PACKAGES=()
SKIPPED_PACKAGES=()
UPDATED_PACKAGES=()

# バージョン比較関数（semver対応）
version_compare() {
    local current="$1"
    local required="$2"
    
    # バージョン文字列を数値配列に変換
    IFS='.' read -ra current_parts <<< "$current"
    IFS='.' read -ra required_parts <<< "$required"
    
    # 配列の長さを揃える
    local max_len=$(( ${#current_parts[@]} > ${#required_parts[@]} ? ${#current_parts[@]} : ${#required_parts[@]} ))
    
    for ((i=0; i<max_len; i++)); do
        local curr=${current_parts[i]:-0}
        local req=${required_parts[i]:-0}
        
        # 数値部分のみ抽出（alphaやrcなどの文字列を除去）
        curr=$(echo "$curr" | sed 's/[^0-9].*$//')
        req=$(echo "$req" | sed 's/[^0-9].*$//')
        
        curr=${curr:-0}
        req=${req:-0}
        
        if [[ $curr -lt $req ]]; then
            return 1  # current < required (アップデート必要)
        elif [[ $curr -gt $req ]]; then
            return 0  # current > required (満足)
        fi
    done
    
    return 0  # current == required (満足)
}

# パッケージの要求バージョンを解析
parse_requirement() {
    local package="$1"
    local package_name=""
    local version_spec=""
    local operator=""
    local required_version=""
    
    # パッケージ名を抽出
    package_name=$(echo "$package" | sed 's/[><=!].*//')
    
    # バージョン指定があるかチェック
    if [[ "$package" == *">="* ]] || [[ "$package" == *">"* ]] || [[ "$package" == *"<="* ]] || [[ "$package" == *"<"* ]] || [[ "$package" == *"=="* ]]; then
        version_spec=$(echo "$package" | sed 's/^[^><=]*//')
        
        # オペレータを抽出
        if [[ "$version_spec" == ">="* ]]; then
            operator=">="
            required_version=$(echo "$version_spec" | sed 's/^>=//')
        elif [[ "$version_spec" == ">"* ]]; then
            operator=">"
            required_version=$(echo "$version_spec" | sed 's/^>//')
        elif [[ "$version_spec" == "<="* ]]; then
            operator="<="
            required_version=$(echo "$version_spec" | sed 's/^<=//')
        elif [[ "$version_spec" == "<"* ]]; then
            operator="<"
            required_version=$(echo "$version_spec" | sed 's/^<//')
        elif [[ "$version_spec" == "=="* ]]; then
            operator="=="
            required_version=$(echo "$version_spec" | sed 's/^==//')
        fi
    fi
    
    echo "$package_name|$operator|$required_version"
}

# パッケージインストール/アップデート関数
install_or_update_package() {
    local package="$1"
    local parsed=$(parse_requirement "$package")
    local package_name=$(echo "$parsed" | cut -d'|' -f1)
    local operator=$(echo "$parsed" | cut -d'|' -f2)
    local required_version=$(echo "$parsed" | cut -d'|' -f3)
    
    echo -e "  📋 Processing: ${BLUE}$package_name${NC}"
    
    # 現在のバージョンをチェック（pip優先）
    local current_version=""
    local install_source=""
    
    if pip show "$package_name" >/dev/null 2>&1; then
        current_version=$(pip show "$package_name" | grep "Version:" | cut -d' ' -f2)
        install_source="pip"
        echo -e "    📦 Current version (pip): $current_version"
    elif conda list "$package_name" >/dev/null 2>&1; then
        local conda_info=$(conda list "$package_name" | grep -E "^$package_name[[:space:]]" | head -1)
        if [[ -n "$conda_info" ]]; then
            current_version=$(echo "$conda_info" | awk '{print $2}')
            install_source="conda"
            echo -e "    📦 Current version (conda): $current_version"
        fi
    fi
    
    # バージョン要求がない場合は、インストール済みならスキップ
    if [[ -z "$required_version" ]]; then
        if [[ -n "$current_version" ]]; then
            echo -e "    ${GREEN}✅ Already installed: $package_name ($current_version)${NC}"
            SKIPPED_PACKAGES+=("$package_name ($install_source: $current_version)")
            return 0
        fi
    else
        # バージョン要求がある場合は比較
        if [[ -n "$current_version" ]]; then
            echo -e "    🔍 Checking version requirement: $operator $required_version"
            
            local needs_update=false
            case "$operator" in
                ">=")
                    if ! version_compare "$current_version" "$required_version"; then
                        needs_update=true
                    fi
                    ;;
                ">")
                    if ! version_compare "$current_version" "$required_version" || [[ "$current_version" == "$required_version" ]]; then
                        needs_update=true
                    fi
                    ;;
                "==")
                    if [[ "$current_version" != "$required_version" ]]; then
                        needs_update=true
                    fi
                    ;;
                "<="|"<")
                    # 通常は最新版を維持するため、これらは警告のみ
                    echo -e "    ${YELLOW}⚠️  Version constraint $operator$required_version may conflict with updates${NC}"
                    ;;
            esac
            
            if [[ "$needs_update" == false ]]; then
                echo -e "    ${GREEN}✅ Version requirement satisfied: $package_name ($current_version)${NC}"
                SKIPPED_PACKAGES+=("$package_name ($install_source: $current_version)")
                return 0
            else
                echo -e "    ${YELLOW}🔄 Version update needed: $current_version → $required_version${NC}"
            fi
        fi
    fi
    
    # インストールまたはアップデート実行
    echo -e "    🔄 Installing/updating: $package"
    
    # pip で試行
    if pip install "$package" --quiet >/dev/null 2>&1; then
        local new_version=$(pip show "$package_name" | grep "Version:" | cut -d' ' -f2 2>/dev/null || echo "unknown")
        if [[ -n "$current_version" ]]; then
            echo -e "    ${GREEN}✅ Updated (pip): $package_name ($current_version → $new_version)${NC}"
            UPDATED_PACKAGES+=("$package_name (pip: $current_version → $new_version)")
        else
            echo -e "    ${GREEN}✅ Installed (pip): $package_name ($new_version)${NC}"
            SUCCESSFUL_PACKAGES+=("$package_name (pip: $new_version)")
        fi
        return 0
    fi
    
    # pip が失敗した場合は conda で試行
    echo -e "    ${YELLOW}⚠️  pip failed, trying conda-forge: $package_name${NC}"
    
    if conda install -c conda-forge "$package_name" -y --quiet >/dev/null 2>&1; then
        local conda_info=$(conda list "$package_name" | grep -E "^$package_name[[:space:]]" | head -1)
        local new_version=$(echo "$conda_info" | awk '{print $2}' 2>/dev/null || echo "unknown")
        if [[ -n "$current_version" ]]; then
            echo -e "    ${GREEN}✅ Updated (conda): $package_name ($current_version → $new_version)${NC}"
            UPDATED_PACKAGES+=("$package_name (conda: $current_version → $new_version)")
        else
            echo -e "    ${GREEN}✅ Installed (conda): $package_name ($new_version)${NC}"
            SUCCESSFUL_PACKAGES+=("$package_name (conda: $new_version)")
        fi
        return 0
    fi
    
    # conda-forge が失敗した場合はデフォルトチャンネル
    echo -e "    ${YELLOW}⚠️  conda-forge failed, trying default conda channel: $package_name${NC}"
    
    if conda install "$package_name" -y --quiet >/dev/null 2>&1; then
        local conda_info=$(conda list "$package_name" | grep -E "^$package_name[[:space:]]" | head -1)
        local new_version=$(echo "$conda_info" | awk '{print $2}' 2>/dev/null || echo "unknown")
        if [[ -n "$current_version" ]]; then
            echo -e "    ${GREEN}✅ Updated (conda-default): $package_name ($current_version → $new_version)${NC}"
            UPDATED_PACKAGES+=("$package_name (conda-default: $current_version → $new_version)")
        else
            echo -e "    ${GREEN}✅ Installed (conda-default): $package_name ($new_version)${NC}"
            SUCCESSFUL_PACKAGES+=("$package_name (conda-default: $new_version)")
        fi
        return 0
    fi
    
    # すべて失敗
    echo -e "    ${RED}❌ All installation methods failed: $package_name${NC}"
    FAILED_PACKAGES+=("$package_name")
    return 1
}

# packages.txt生成関数（修正版）
generate_packages_txt() {
    echo -e "\n${BLUE}📝 Generating packages.txt...${NC}"
    
    packages_file="packages.txt"
    
    # 一時的にエラーハンドリングを無効化
    set +e
    
    # ヘッダー作成
    cat > "$packages_file" << EOF
# ==============================================================================
# 📦 INSTALLED PACKAGES INVENTORY
# ==============================================================================
# Generated on: $(date '+%Y-%m-%d %H:%M:%S')
# Environment: $CONDA_DEFAULT_ENV
# Python: $(python --version 2>&1)
# ==============================================================================

EOF

    # PIPパッケージセクション
    echo "# 🐍 PIP PACKAGES" >> "$packages_file"
    echo "# =============================================================================" >> "$packages_file"
    
    # pipパッケージを取得
    pip_packages=$(pip list --format=freeze 2>/dev/null)
    pip_count=0
    
    if [[ -n "$pip_packages" ]]; then
        while IFS= read -r line; do
            if [[ -n "$line" && "$line" != *"#"* && "$line" == *"=="* ]]; then
                package_name=$(echo "$line" | cut -d'=' -f1)
                package_version=$(echo "$line" | cut -d'=' -f3)
                
                # 美しい形式で出力
                printf "%-40s # pip: %s\n" "$line" "$package_version" >> "$packages_file"
                ((pip_count++))
            fi
        done <<< "$(echo "$pip_packages" | sort)"
    fi
    
    echo "" >> "$packages_file"
    echo "# Total PIP packages: $pip_count" >> "$packages_file"
    echo "" >> "$packages_file"
    
    # Condaパッケージセクション
    echo "# 🐍 CONDA PACKAGES (non-pip)" >> "$packages_file"
    echo "# =============================================================================" >> "$packages_file"
    
    # condaパッケージを取得（pip以外）
    conda_packages=$(conda list --no-pip 2>/dev/null | tail -n +4)
    conda_count=0
    
    if [[ -n "$conda_packages" ]]; then
        while IFS= read -r line; do
            if [[ -n "$line" && "$line" != "#"* ]]; then
                # 空白で分割
                read -r package_name package_version package_build package_channel <<< "$line"
                
                # パッケージ名とバージョンが有効かチェック
                if [[ -n "$package_name" && -n "$package_version" ]]; then
                    # チャンネル情報を整理
                    if [[ -z "$package_channel" ]]; then
                        package_channel="defaults"
                    fi
                    
                    # 美しい形式で出力
                    printf "%-40s # conda: %s (%s)\n" "$package_name==$package_version" "$package_version" "$package_channel" >> "$packages_file"
                    ((conda_count++))
                fi
            fi
        done <<< "$(echo "$conda_packages" | sort)"
    fi
    
    echo "" >> "$packages_file"
    echo "# Total Conda packages: $conda_count" >> "$packages_file"
    echo "" >> "$packages_file"
    
    # サマリーセクション
    cat >> "$packages_file" << EOF
# ==============================================================================
# 📊 SUMMARY
# ==============================================================================
# Environment: $CONDA_DEFAULT_ENV
# Python Version: $(python --version 2>&1 | cut -d' ' -f2)
# Python Executable: $(which python)
# Total PIP packages: $pip_count
# Total Conda packages: $conda_count
# Total packages: $((pip_count + conda_count))
# Last updated: $(date '+%Y-%m-%d %H:%M:%S')
# ==============================================================================
EOF
    
    # エラーハンドリングを再有効化
    set -e
    
    echo -e "${GREEN}✅ packages.txt generated successfully!${NC}"
    echo -e "${CYAN}   📄 File: $packages_file${NC}"
    echo -e "${CYAN}   📊 PIP packages: $pip_count${NC}"
    echo -e "${CYAN}   📊 Conda packages: $conda_count${NC}"
    echo -e "${CYAN}   📊 Total: $((pip_count + conda_count))${NC}"
    
    # 生成されたファイルの先頭を表示
    echo -e "\n${YELLOW}📋 Generated packages.txt preview:${NC}"
    head -20 "$packages_file" | while IFS= read -r line; do
        echo -e "${CYAN}   $line${NC}"
    done
    echo -e "${CYAN}   ... (and more)${NC}"
}

# 環境状態確認
echo -e "${BLUE}🔍 Checking current environment status...${NC}"
pip_count=$(pip list 2>/dev/null | wc -l || echo "0")
conda_count=$(conda list 2>/dev/null | wc -l || echo "0")
echo -e "${YELLOW}Current packages: pip($pip_count), conda($conda_count)${NC}"

# メイン処理開始
echo -e "\n${BLUE}📂 Searching for requirements.txt files...${NC}"
REQUIREMENTS_FILES=$(find . -name "requirements.txt" -type f)

if [[ -z "$REQUIREMENTS_FILES" ]]; then
    echo -e "${YELLOW}⚠️  No requirements.txt files found${NC}"
    # requirements.txtがなくてもpackages.txtは生成
    generate_packages_txt
    exit 0
fi

echo -e "${GREEN}Found requirements.txt files:${NC}"
while IFS= read -r file; do
    echo -e "  📄 $file"
done <<< "$REQUIREMENTS_FILES"

# topgunを最初にインストール
if [[ -d "topgun" ]]; then
    echo -e "\n${BLUE}📦 Installing topgun (editable)...${NC}"
    
    if pip show topgun >/dev/null 2>&1; then
        topgun_version=$(pip show topgun | grep "Version:" | cut -d' ' -f2)
        echo -e "${GREEN}✅ topgun already installed ($topgun_version)${NC}"
        SKIPPED_PACKAGES+=("topgun (already installed: $topgun_version)")
    else
        # setup.pyまたはpyproject.tomlが存在するかチェック
        if [[ -f "topgun/setup.py" ]] || [[ -f "topgun/pyproject.toml" ]]; then
            echo -e "    🔄 Installing topgun in editable mode..."
            
            # エラー出力付きでインストール試行
            if pip install -e topgun/ 2>/dev/null; then
                new_topgun_version=$(pip show topgun | grep "Version:" | cut -d' ' -f2 2>/dev/null || echo "dev")
                echo -e "${GREEN}✅ topgun installation successful ($new_topgun_version)${NC}"
                SUCCESSFUL_PACKAGES+=("topgun (editable: $new_topgun_version)")
            else
                echo -e "${RED}❌ topgun installation failed${NC}"
                echo -e "${YELLOW}    ℹ️  Check if topgun/setup.py or topgun/pyproject.toml exists and is valid${NC}"
                
                # デバッグ情報を表示
                echo -e "${YELLOW}    🔍 Debug: Checking topgun directory contents:${NC}"
                ls -la topgun/ 2>/dev/null | head -5 | while IFS= read -r line; do
                    echo -e "${YELLOW}       $line${NC}"
                done
                
                FAILED_PACKAGES+=("topgun")
            fi
        else
            echo -e "${YELLOW}⚠️  topgun directory found but no setup.py or pyproject.toml${NC}"
            echo -e "${YELLOW}    ℹ️  Skipping topgun installation${NC}"
            SKIPPED_PACKAGES+=("topgun (no setup files found)")
        fi
    fi
fi

# 重複パッケージを避けるためのセット
declare -A PROCESSED_PACKAGES

# 各requirements.txtファイルを処理
while IFS= read -r requirements_file; do
    echo -e "\n${BLUE}📦 Processing: $requirements_file${NC}"
    
    # コメント行と空行を除外してパッケージを抽出
    packages=$(grep -v '^#' "$requirements_file" | grep -v '^$' | sed 's/[[:space:]]*#.*$//')
    
    if [[ -z "$packages" ]]; then
        echo -e "${YELLOW}  ⚠️  No packages found in $requirements_file${NC}"
        continue
    fi
    
    # パッケージを一つずつ処理
    while IFS= read -r package; do
        if [[ -z "$package" ]]; then
            continue
        fi
        
        # パッケージ名を抽出
        package_name=$(echo "$package" | sed 's/[><=!].*//')
        
        # 重複チェック
        if [[ -n "${PROCESSED_PACKAGES[$package_name]:-}" ]]; then
            echo -e "  ${YELLOW}⏭️  Skipping already processed: $package_name${NC}"
            continue
        fi
        
        # パッケージをインストール/アップデート
        install_or_update_package "$package"
        PROCESSED_PACKAGES[$package_name]=1
    done <<< "$packages"
done <<< "$REQUIREMENTS_FILES"

# 結果報告
echo -e "\n${GREEN}🎉 Installation/update process completed!${NC}"

# スキップされたパッケージの報告
if [[ ${#SKIPPED_PACKAGES[@]} -gt 0 ]]; then
    echo -e "\n${CYAN}⏭️  Skipped packages (requirements satisfied):${NC}"
    printf '  %s\n' "${SKIPPED_PACKAGES[@]}"
fi

# 新規インストールされたパッケージの報告
if [[ ${#SUCCESSFUL_PACKAGES[@]} -gt 0 ]]; then
    echo -e "\n${GREEN}✅ Newly installed packages:${NC}"
    printf '  %s\n' "${SUCCESSFUL_PACKAGES[@]}"
fi

# アップデートされたパッケージの報告
if [[ ${#UPDATED_PACKAGES[@]} -gt 0 ]]; then
    echo -e "\n${BLUE}🔄 Updated packages:${NC}"
    printf '  %s\n' "${UPDATED_PACKAGES[@]}"
fi

# 失敗したパッケージの報告
if [[ ${#FAILED_PACKAGES[@]} -gt 0 ]]; then
    echo -e "\n${RED}❌ Failed packages:${NC}"
    printf '  %s\n' "${FAILED_PACKAGES[@]}"
fi

# 統計
echo -e "\n${BLUE}📊 Session Statistics:${NC}"
echo -e "${CYAN}Skipped (satisfied):${NC} ${#SKIPPED_PACKAGES[@]}"
echo -e "${GREEN}Newly installed:${NC} ${#SUCCESSFUL_PACKAGES[@]}"
echo -e "${BLUE}Updated:${NC} ${#UPDATED_PACKAGES[@]}"
echo -e "${RED}Failed:${NC} ${#FAILED_PACKAGES[@]}"

# 主要パッケージの確認（修正版）
echo -e "\n${YELLOW}Key packages check:${NC}"
key_packages=("rich" "aiohttp" "pandas" "numpy" "matplotlib" "topgun" "marshmallow" "marshmallow-dataclass" "mypy" "typing-extensions")

for pkg in "${key_packages[@]}"; do
    if pip_version=$(pip show "$pkg" 2>/dev/null | grep "Version:" | cut -d' ' -f2); then
        if [[ -n "$pip_version" ]]; then
            echo -e "  ${GREEN}✅ $pkg${NC} ${BLUE}(pip: $pip_version)${NC}"
        else
            echo -e "  ${YELLOW}⚠️  $pkg${NC} ${YELLOW}(pip: version unknown)${NC}"
        fi
    elif conda_info=$(conda list "$pkg" 2>/dev/null | grep -E "^$pkg[[:space:]]" | head -1); then
        if [[ -n "$conda_info" ]]; then
            conda_version=$(echo "$conda_info" | awk '{print $2}')
            if [[ -n "$conda_version" ]]; then
                echo -e "  ${GREEN}✅ $pkg${NC} ${PURPLE}(conda: $conda_version)${NC}"
            else
                echo -e "  ${YELLOW}⚠️  $pkg${NC} ${PURPLE}(conda: version unknown)${NC}"
            fi
        else
            echo -e "  ${RED}❌ $pkg (not found)${NC}"
        fi
    else
        echo -e "  ${RED}❌ $pkg (not found)${NC}"
    fi
done

# packages.txt生成（必ず実行）
generate_packages_txt

echo -e "\n${GREEN}✅ All done! Environment is ready for development.${NC}"

if [[ ${#SKIPPED_PACKAGES[@]} -gt 0 ]]; then
    echo -e "${BLUE}⚡ Next run will be faster - most packages already satisfied!${NC}"
fi

# 最終実行時刻の記録
echo -e "\n${YELLOW}📅 Last updated: $(date '+%Y-%m-%d %H:%M:%S')${NC}"