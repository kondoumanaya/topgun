"""
topgun型エラー完全修正スクリプト
mypyエラー「missing library stubs or py.typed marker」を解決
"""

import os
import subprocess
import sys
from pathlib import Path

def create_type_files():
    """型情報ファイルの作成"""
    print("🔧 型情報ファイル作成開始...")
    
    base_path = Path("/Users/manayakondou/Documents/workspace/root-bot/topgun/topgun")
    
    # 1. メインのpy.typedを確認・更新
    main_py_typed = base_path / "py.typed"
    if not main_py_typed.exists() or not main_py_typed.read_text().strip():
        main_py_typed.write_text("partial\n")
        print(f"✅ Created/Updated: {main_py_typed}")
    
    # 2. helpersディレクトリのpy.typed作成
    helpers_dir = base_path / "helpers"
    helpers_py_typed = helpers_dir / "py.typed"
    helpers_py_typed.write_text("partial\n")
    print(f"✅ Created: {helpers_py_typed}")
    
    # 3. bitbank.pyi型スタブ作成
    bitbank_pyi = helpers_dir / "bitbank.pyi"
    bitbank_stub_content = '''"""
Type stubs for topgun.helpers.bitbank
Generated to resolve mypy import-untyped errors
"""
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union
import topgun

async def subscribe_with_callback(
    client: topgun.Client,
    callback: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]
) -> None:
    """
    Subscribe to bitbank WebSocket with callback function
    
    Args:
        client: Topgun client instance with bitbank API credentials
        callback: Async callback function to handle WebSocket messages
        
    Returns:
        None - runs indefinitely until cancelled
    """
    ...

async def get_user_info(client: topgun.Client) -> Dict[str, Any]:
    """Get user account information"""
    ...

async def get_balance(client: topgun.Client) -> Dict[str, Any]:
    """Get account balance information"""
    ...

async def get_active_orders(
    client: topgun.Client,
    pair: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get active orders"""
    ...

async def get_order_history(
    client: topgun.Client,
    pair: str,
    count: Optional[int] = None,
    from_id: Optional[int] = None,
    end_id: Optional[int] = None,
    since: Optional[int] = None,
    end: Optional[int] = None,
    order: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get order history"""
    ...

async def place_order(
    client: topgun.Client,
    pair: str,
    amount: str,
    price: str,
    side: str,
    type: str,
    post_only: Optional[bool] = None
) -> Dict[str, Any]:
    """Place a new order"""
    ...

async def cancel_order(
    client: topgun.Client,
    pair: str,
    order_id: int
) -> Dict[str, Any]:
    """Cancel an order"""
    ...

async def cancel_all_orders(
    client: topgun.Client,
    pair: str
) -> Dict[str, Any]:
    """Cancel all orders for a trading pair"""
    ...

def create_websocket_url(base_url: str, endpoint: str) -> str:
    """Create WebSocket URL"""
    ...

def format_timestamp(timestamp: Union[int, float]) -> str:
    """Format timestamp for API requests"""
    ...
'''
    
    bitbank_pyi.write_text(bitbank_stub_content)
    print(f"✅ Created: {bitbank_pyi}")
    
    # 4. helpers/__init__.pyi作成
    helpers_init_pyi = helpers_dir / "__init__.pyi"
    helpers_init_content = '''"""
Type stubs for topgun.helpers module
"""
from . import bitbank as bitbank

__all__ = ["bitbank"]
'''
    helpers_init_pyi.write_text(helpers_init_content)
    print(f"✅ Created: {helpers_init_pyi}")
    
    return True

def create_mypy_config():
    """mypy設定ファイルの作成/更新"""
    print("\n🔧 mypy設定ファイル作成...")
    
    config_path = Path("/Users/manayakondou/Documents/workspace/root-bot/pyproject.toml")
    
    mypy_config = '''
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
show_error_codes = true

# topgun パッケージの設定
[[tool.mypy.overrides]]
module = "topgun.*"
ignore_missing_imports = false

# 外部ライブラリの設定
[[tool.mypy.overrides]]
module = [
    "aiohttp.*",
    "websockets.*",
    "asyncio.*"
]
ignore_missing_imports = true
'''
    
    if config_path.exists():
        content = config_path.read_text()
        if "[tool.mypy]" not in content:
            with open(config_path, "a") as f:
                f.write(mypy_config)
            print(f"✅ Added mypy config to: {config_path}")
        else:
            print(f"⚠️  mypy config already exists in: {config_path}")
    else:
        config_path.write_text(mypy_config)
        print(f"✅ Created: {config_path}")
    
    return config_path.exists()

def verify_files():
    """作成されたファイルの確認"""
    print("\n🔍 作成ファイル確認...")
    
    base_path = Path("/Users/manayakondou/Documents/workspace/root-bot/topgun/topgun")
    
    files_to_check = [
        (base_path / "py.typed", "Main py.typed marker"),
        (base_path / "helpers" / "py.typed", "Helpers py.typed marker"),
        (base_path / "helpers" / "bitbank.pyi", "Bitbank type stub"),
        (base_path / "helpers" / "__init__.pyi", "Helpers init stub"),
    ]
    
    all_good = True
    for file_path, description in files_to_check:
        if file_path.exists() and file_path.stat().st_size > 0:
            size = file_path.stat().st_size
            print(f"✅ {description}: OK ({size} bytes)")
        else:
            print(f"❌ {description}: Missing or empty")
            all_good = False
    
    return all_good

def test_mypy():
    """mypy テストの実行"""
    print("\n🧪 mypy テスト実行...")
    
    test_file = "/Users/manayakondou/Documents/workspace/root-bot/topgun/examples/helpers/bitbank.py"
    
    if not Path(test_file).exists():
        print(f"❌ テストファイルが見つかりません: {test_file}")
        return False
    
    try:
        # mypy実行
        cmd = [
            sys.executable, "-m", "mypy",
            "--show-error-codes",
            "--pretty",
            test_file
        ]
        
        result = subprocess.run(
            cmd,
            cwd="/Users/manayakondou/Documents/workspace/root-bot",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ mypy チェック成功! エラーなし")
            return True
        else:
            print("⚠️  mypy チェック結果:")
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ mypy が見つかりません")
        print("以下のコマンドでインストール:")
        print("pip install mypy")
        return False
    except Exception as e:
        print(f"❌ mypy テスト実行エラー: {e}")
        return False

def test_import():
    """インポートテストの実行"""
    print("\n🧪 インポートテスト実行...")
    
    try:
        # プロジェクトルートをパスに追加
        project_root = "/Users/manayakondou/Documents/workspace/root-bot"
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # インポートテスト
        from topgun.helpers.bitbank import subscribe_with_callback
        print("✅ subscribe_with_callback インポート成功")
        print(f"   Function type: {type(subscribe_with_callback)}")
        print(f"   Function module: {subscribe_with_callback.__module__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("topgunパッケージの構造を確認")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def show_next_steps():
    """次のステップの表示"""
    print("\n🎯 次のステップ:")
    print("1. VSCodeでPython Language Serverをリスタート:")
    print("   Ctrl+Shift+P → 'Python: Restart Language Server'")
    print("")
    print("2. エラーが消えているか確認:")
    print("   topgun/examples/helpers/bitbank.py を開く")
    print("")
    print("3. 追加のmypyテスト:")
    print("   mypy topgun/examples/helpers/bitbank.py")
    print("")
    print("4. 実際の動作確認:")
    print("   python topgun/examples/helpers/bitbank.py")
    print("   (環境変数 BITBANK_API_KEY, BITBANK_API_SECRET が必要)")

def main():
    """メイン実行関数"""
    print("🚀 topgun 型エラー修正スクリプト開始")
    print("=" * 60)
    print("目的: 'missing library stubs or py.typed marker' エラーの解決")
    print("")
    
    success_count = 0
    total_steps = 5
    
    try:
        # ステップ1: 型ファイル作成
        if create_type_files():
            success_count += 1
            print("✅ ステップ1完了: 型ファイル作成")
        
        # ステップ2: mypy設定
        if create_mypy_config():
            success_count += 1
            print("✅ ステップ2完了: mypy設定")
        
        # ステップ3: ファイル確認
        if verify_files():
            success_count += 1
            print("✅ ステップ3完了: ファイル確認")
        
        # ステップ4: インポートテスト
        if test_import():
            success_count += 1
            print("✅ ステップ4完了: インポートテスト")
        
        # ステップ5: mypyテスト
        if test_mypy():
            success_count += 1
            print("✅ ステップ5完了: mypyテスト")
        
        # 結果表示
        print(f"\n📊 修正結果: {success_count}/{total_steps} ステップ成功")
        
        if success_count == total_steps:
            print("🎉 全ての修正が完了しました!")
            show_next_steps()
        elif success_count >= 3:
            print("⚠️  部分的に成功しました。手動での追加設定が必要な場合がある。")
            show_next_steps()
        else:
            print("❌ 修正に失敗しました。手動での対応が必要 。")
            print("\n手動修正方法:")
            print("1. topgun/topgun/helpers/py.typed ファイルを作成")
            print("2. topgun/topgun/helpers/bitbank.pyi ファイルを作成")
            print("3. VSCode Language Server をリスタート")
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
