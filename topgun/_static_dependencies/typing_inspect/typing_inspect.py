"""Defines experimental API for runtime inspection of types defined
in the standard "typing" module.

Example usage::
    from typing_inspect import is_generic_type
"""

import types
import collections.abc
import typing_extensions

# 公開APIを使用した型定義の取得
from mypy_extensions import TypedDict
_TypedDictMeta_Mypy = type(TypedDict)

from typing_extensions import TypedDict as TypedDict_TE
_TypedDictMeta_TE = type(TypedDict_TE)

# Python 3.12でのインポート
from typing import (
    Generic, Callable, Union, TypeVar, ClassVar, Tuple,
    ForwardRef, NewType, get_origin as typing_get_origin,
    List
)
from types import GenericAlias as _GenericAlias
from typing_extensions import Final, Literal

# Python 3.9以降の特殊型の処理
special_origin = typing_get_origin(List)
from typing import _SpecialForm  # type: ignore

# Union型の処理
MaybeUnionType = types.UnionType

# GenericAliasの型定義
typingGenericAlias = (_GenericAlias, _SpecialForm, types.GenericAlias)

# リテラル型の判定に使用するセット
LITERALS = {Literal}

def is_generic_type(tp):
    """Test if the given type is a generic type. This includes Generic itself, but
    excludes special typing constructs such as Union, Tuple, Callable, ClassVar.
    Examples::

        is_generic_type(int) == False
        is_generic_type(Union[int, str]) == False
        is_generic_type(Union[int, T]) == False
        is_generic_type(ClassVar[List[int]]) == False
        is_generic_type(Callable[..., T]) == False

        is_generic_type(Generic) == True
        is_generic_type(Generic[T]) == True
        is_generic_type(Iterable[int]) == True
        is_generic_type(Mapping) == True
        is_generic_type(MutableMapping[T, List[int]]) == True
        is_generic_type(Sequence[Union[str, bytes]]) == True
    """
    return (isinstance(tp, type) and issubclass(tp, Generic) or
            isinstance(tp, typingGenericAlias) and
            tp.__origin__ not in (Union, tuple, ClassVar, collections.abc.Callable))


def is_callable_type(tp):
    """Test if the type is a generic callable type, including subclasses
    excluding non-generic types and callables.
    Examples::

        is_callable_type(int) == False
        is_callable_type(type) == False
        is_callable_type(Callable) == True
        is_callable_type(Callable[..., int]) == True
        is_callable_type(Callable[[int, int], Iterable[str]]) == True
        class MyClass(Callable[[int], int]):
            ...
        is_callable_type(MyClass) == True

    For more general tests use callable(), for more precise test
    (excluding subclasses) use::

        get_origin(tp) is collections.abc.Callable
    """
    return (tp is Callable or isinstance(tp, typingGenericAlias) and
            tp.__origin__ is collections.abc.Callable or
            isinstance(tp, type) and issubclass(tp, Generic) and
            issubclass(tp, collections.abc.Callable))


def is_tuple_type(tp):
    """Test if the type is a generic tuple type, including subclasses excluding
    non-generic classes.
    Examples::

        is_tuple_type(int) == False
        is_tuple_type(tuple) == False
        is_tuple_type(Tuple) == True
        is_tuple_type(Tuple[str, int]) == True
        class MyClass(Tuple[str, int]):
            ...
        is_tuple_type(MyClass) == True

    For more general tests use issubclass(..., tuple), for more precise test
    (excluding subclasses) use::

        get_origin(tp) is tuple
    """
    return (tp is Tuple or isinstance(tp, typingGenericAlias) and
            tp.__origin__ is tuple or
            isinstance(tp, type) and issubclass(tp, Generic) and
            issubclass(tp, tuple))


def is_optional_type(tp):
    """Test if the type is type(None), or is a direct union with it, such as Optional[T].

    NOTE: this method inspects nested `Union` arguments but not `TypeVar` definition
    bounds and constraints. So it will return `False` if
    - `tp` is a `TypeVar` bound, or constrained to, an optional type
    - `tp` is a `Union` to a `TypeVar` bound or constrained to an optional type,
    - `tp` refers to a *nested* `Union` containing an optional type or one of the above.

    Users wishing to check for optionality in types relying on type variables might wish
    to use this method in combination with `get_constraints` and `get_bound`
    """
    if tp is type(None):  # noqa
        return True
    elif is_union_type(tp):
        return any(is_optional_type(tt) for tt in get_args(tp))
    else:
        return False


def is_final_type(tp):
    """Test if the type is a final type. Examples::

        is_final_type(int) == False
        is_final_type(Final) == True
        is_final_type(Final[int]) == True
    """
    return (tp is Final or
            isinstance(tp, typingGenericAlias) and tp.__origin__ is Final)


def is_union_type(tp):
    """Test if the type is a union type. Examples::

        is_union_type(int) == False
        is_union_type(Union) == True
        is_union_type(Union[int, int]) == False
        is_union_type(Union[T, int]) == True
        is_union_type(int | int) == False
        is_union_type(T | int) == True
    """
    return (tp is Union or
            (isinstance(tp, typingGenericAlias) and tp.__origin__ is Union) or
            isinstance(tp, MaybeUnionType))


def is_literal_type(tp):
    """Test if the type is a literal type."""
    return (tp in LITERALS or
            isinstance(tp, typingGenericAlias) and tp.__origin__ in LITERALS)


def is_typevar(tp):
    """Test if the type represents a type variable. Examples::

        is_typevar(int) == False
        is_typevar(T) == True
        is_typevar(Union[T, int]) == False
    """
    return type(tp) is TypeVar


def is_classvar(tp):
    """Test if the type represents a class variable. Examples::

        is_classvar(int) == False
        is_classvar(ClassVar) == True
        is_classvar(ClassVar[int]) == True
        is_classvar(ClassVar[List[T]]) == True
    """
    return (tp is ClassVar or
            isinstance(tp, typingGenericAlias) and tp.__origin__ is ClassVar)


def is_new_type(tp):
    """Tests if the type represents a distinct type. Examples::

        is_new_type(int) == False
        is_new_type(NewType) == True
        is_new_type(NewType('Age', int)) == True
        is_new_type(NewType('Scores', List[Dict[str, float]])) == True
    """
    return (tp in (NewType, typing_extensions.NewType) or
            isinstance(tp, (NewType, typing_extensions.NewType)))


def is_forward_ref(tp):
    """Tests if the type is a :class:`typing.ForwardRef`. Examples::

        u = Union["Milk", Way]
        args = get_args(u)
        is_forward_ref(args[0]) == True
        is_forward_ref(args[1]) == False
    """
    return isinstance(tp, ForwardRef)


def get_origin(tp):
    """Get the unsubscripted version of a type. Supports generic types, Union,
    Callable, and Tuple. Returns None for unsupported types. Examples::

        get_origin(int) == None
        get_origin(ClassVar[int]) == None
        get_origin(Generic) == Generic
        get_origin(Generic[T]) == Generic
        get_origin(Union[T, int]) == Union
        get_origin(List[Tuple[T, T]][int]) == list
    """
    if isinstance(tp, typingGenericAlias):
        return tp.__origin__ if tp.__origin__ is not ClassVar else None
    if tp is Generic:
        return Generic
    return None


def get_parameters(tp):
    """Return type parameters of a parameterizable type as a tuple
    in lexicographic order. Parameterizable types are generic types,
    unions, tuple types and callable types. Examples::

        get_parameters(int) == ()
        get_parameters(Generic) == ()
        get_parameters(Union) == ()
        get_parameters(List[int]) == ()

        get_parameters(Generic[T]) == (T,)
        get_parameters(Tuple[List[T], List[S_co]]) == (T, S_co)
        get_parameters(Union[S_co, Tuple[T, T]][int, U]) == (U,)
        get_parameters(Mapping[T, Tuple[S_co, T]]) == (T, S_co)
    """
    if (
            (
                isinstance(tp, typingGenericAlias) and
                hasattr(tp, '__parameters__')
            ) or
            isinstance(tp, type) and issubclass(tp, Generic) and
            tp is not Generic):
        return tp.__parameters__
    else:
        return ()


def get_args(tp, evaluate=True):
    """Get type arguments with all substitutions performed. For unions,
    basic simplifications used by Union constructor are performed.
    On Python 3.7+ the `evaluate` parameter is ignored.

    Examples::
        get_args(int) == ()
        get_args(Union[int, str]) == (int, str)
        get_args(Dict[int, Tuple[T, T]][str]) == (int, Tuple[str, str])
    """
    # Python 3.12ではevaluateは無視される
    if isinstance(tp, typingGenericAlias) and hasattr(tp, '__args__'):
        res = tp.__args__
        if get_origin(tp) is collections.abc.Callable and res[0] is not Ellipsis:
            res = (list(res[:-1]), res[-1])
        return res
    if isinstance(tp, MaybeUnionType):
        return tp.__args__
    return ()


def get_bound(tp):
    """Return the type bound to a `TypeVar` if any.

    It the type is not a `TypeVar`, a `TypeError` is raised.
    Examples::

        get_bound(TypeVar('T')) == None
        get_bound(TypeVar('T', bound=int)) == int
    """
    if is_typevar(tp):
        return getattr(tp, '__bound__', None)
    else:
        raise TypeError("type is not a `TypeVar`: " + str(tp))


def get_constraints(tp):
    """Returns the constraints of a `TypeVar` if any.

    It the type is not a `TypeVar`, a `TypeError` is raised
    Examples::

        get_constraints(TypeVar('T')) == ()
        get_constraints(TypeVar('T', int, str)) == (int, str)
    """
    if is_typevar(tp):
        return getattr(tp, '__constraints__', ())
    else:
        raise TypeError("type is not a `TypeVar`: " + str(tp))


def get_generic_type(obj):
    """Get the generic type of an object if possible, or runtime class otherwise.
    Examples::

        class Node(Generic[T]):
            ...
        type(Node[int]()) == Node
        get_generic_type(Node[int]()) == Node[int]
        get_generic_type(Node[T]()) == Node[T]
        get_generic_type(1) == int
    """
    gen_type = getattr(obj, '__orig_class__', None)
    return gen_type if gen_type is not None else type(obj)


def get_generic_bases(tp):
    """Get generic base types of a type or empty tuple if not possible.
    Example::

        class MyClass(List[int], Mapping[str, List[int]]):
            ...
        MyClass.__bases__ == (List, Mapping)
        get_generic_bases(MyClass) == (List[int], Mapping[str, List[int]])
    """
    return getattr(tp, '__orig_bases__', ())


def typed_dict_keys(td):
    """If td is a TypedDict class, return a dictionary mapping the typed keys to types.
    Otherwise, return None. Examples::

        class TD(TypedDict):
            x: int
            y: int
        class Other(dict):
            x: int
            y: int

        typed_dict_keys(TD) == {'x': int, 'y': int}
        typed_dict_keys(dict) == None
        typed_dict_keys(Other) == None
    """
    if isinstance(td, (_TypedDictMeta_Mypy, _TypedDictMeta_TE)):
        return td.__annotations__.copy()
    return None


def get_forward_arg(fr):
    """
    If fr is a ForwardRef, return the string representation of the forward reference.
    Otherwise return None. Examples::

        tp = List["FRef"]
        fr = get_args(tp)[0]
        get_forward_arg(fr) == "FRef"
        get_forward_arg(tp) == None
    """
    return fr.__forward_arg__ if is_forward_ref(fr) else None