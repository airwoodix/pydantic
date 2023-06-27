from __future__ import annotations as _annotations

import collections
import typing
from collections import deque
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Pattern, Sequence, Type
from uuid import UUID

from pydantic_core import CoreSchema, core_schema
from typing_extensions import TypedDict

from pydantic import ByteSize
from pydantic.networks import IPv4Address, IPv4Interface, IPv4Network, IPv6Address, IPv6Interface, IPv6Network


@dataclass
class Row:
    field_type: type[Any]
    input_type: type[Any]
    mode: Literal['Lax', 'Strict']
    input_format: Literal['Python', 'JSON', 'Python & JSON']
    condition: str | None = None
    valid_examples: list[Any] | None = None
    invalid_examples: list[Any] | None = None
    core_schemas: list[type[CoreSchema]] | None = None


table: list[Row] = [
    Row(
        str,
        str,
        'Strict',
        'Python & JSON',
        core_schemas=[core_schema.StringSchema],
    ),
    Row(
        str,
        bytes,
        'Lax',
        'Python',
        condition='Assumes UTF-8, error on unicode decoding error.',
        valid_examples=[b'this is bytes'],
        invalid_examples=[b'\x81'],
        core_schemas=[core_schema.StringSchema],
    ),
    Row(
        str,
        bytearray,
        'Lax',
        'Python',
        condition='Assumes UTF-8, error on unicode decoding error.',
        valid_examples=[bytearray(b'this is bytearray' * 3)],
        invalid_examples=[bytearray(b'\x81' * 5)],
        core_schemas=[core_schema.StringSchema],
    ),
    Row(
        bytes,
        bytes,
        'Strict',
        'Python',
        core_schemas=[core_schema.BytesSchema],
    ),
    Row(
        bytes,
        str,
        'Strict',
        'JSON',
        valid_examples=['foo'],
        core_schemas=[core_schema.BytesSchema],
    ),
    Row(
        bytes,
        str,
        'Lax',
        'Python',
        valid_examples=['foo'],
        core_schemas=[core_schema.BytesSchema],
    ),
    Row(
        bytes,
        bytearray,
        'Lax',
        'Python',
        valid_examples=[bytearray(b'this is bytearray' * 3)],
        core_schemas=[core_schema.BytesSchema],
    ),
    Row(
        int,
        int,
        'Strict',
        'Python & JSON',
        condition='Max abs value `2^64` - `i64` is used internally, `bool` explicitly forbidden.',
        invalid_examples=[2**64, True, False],
        core_schemas=[core_schema.IntSchema],
    ),
    Row(
        int,
        int,
        'Lax',
        'Python & JSON',
        condition='`i64`. Limits `numbers > (2 ^ 63) - 1` to `(2 ^ 63) - 1`.',
        core_schemas=[core_schema.IntSchema],
    ),
    Row(
        int,
        float,
        'Lax',
        'Python & JSON',
        condition='`i64`, Must be exact int, e.g. `val % 1 == 0`, raises error for `nan`, `inf`.',
        valid_examples=[2.0],
        invalid_examples=[2.1, 2.2250738585072011e308, float('nan'), float('inf')],
        core_schemas=[core_schema.IntSchema],
    ),
    Row(
        int,
        Decimal,
        'Lax',
        'Python',
        condition='`i64`, Must be exact int, e.g. `val % 1 == 0`.',
        valid_examples=[Decimal(2.0)],
        invalid_examples=[Decimal(2.1)],
        core_schemas=[core_schema.IntSchema],
    ),
    Row(
        int,
        bool,
        'Lax',
        'Python & JSON',
        valid_examples=[True, False],
        core_schemas=[core_schema.IntSchema],
    ),
    Row(
        int,
        str,
        'Lax',
        'Python & JSON',
        condition='`i64`, Must be numeric only, e.g. `[0-9]+`.',
        valid_examples=['123'],
        invalid_examples=['test', '123x'],
        core_schemas=[core_schema.IntSchema],
    ),
    Row(
        int,
        bytes,
        'Lax',
        'Python',
        condition='`i64`, Must be numeric only, e.g. `[0-9]+`.',
        valid_examples=[b'123'],
        invalid_examples=[b'test', b'123x'],
        core_schemas=[core_schema.IntSchema],
    ),
    Row(
        float,
        float,
        'Strict',
        'Python & JSON',
        condition='`bool` explicitly forbidden.',
        invalid_examples=[True, False],
        core_schemas=[core_schema.FloatSchema],
    ),
    Row(
        float,
        int,
        'Strict',
        'Python & JSON',
        valid_examples=[123],
        core_schemas=[core_schema.FloatSchema],
    ),
    Row(
        float,
        str,
        'Lax',
        'Python & JSON',
        condition='Must match `[0-9]+(\\.[0-9]+)?`.',
        valid_examples=['3.141'],
        invalid_examples=['test', '3.141x'],
        core_schemas=[core_schema.FloatSchema],
    ),
    Row(
        float,
        bytes,
        'Lax',
        'Python',
        condition='Must match `[0-9]+(\\.[0-9]+)?`.',
        valid_examples=[b'3.141'],
        invalid_examples=[b'test', b'3.141x'],
        core_schemas=[core_schema.FloatSchema],
    ),
    Row(
        float,
        Decimal,
        'Lax',
        'Python',
        valid_examples=[Decimal(3.5)],
        core_schemas=[core_schema.FloatSchema],
    ),
    Row(
        float,
        bool,
        'Lax',
        'Python & JSON',
        valid_examples=[True, False],
        core_schemas=[core_schema.FloatSchema],
    ),
    Row(
        bool,
        bool,
        'Strict',
        'Python & JSON',
        valid_examples=[True, False],
        core_schemas=[core_schema.BoolSchema],
    ),
    Row(
        bool,
        int,
        'Lax',
        'Python & JSON',
        condition='Allowed values: `0, 1`.',
        valid_examples=[0, 1],
        invalid_examples=[2, 100],
        core_schemas=[core_schema.BoolSchema],
    ),
    Row(
        bool,
        float,
        'Lax',
        'Python & JSON',
        condition='Allowed values: `0.0, 1.0`.',
        valid_examples=[0.0, 1.0],
        invalid_examples=[2.0, 100.0],
        core_schemas=[core_schema.BoolSchema],
    ),
    Row(
        bool,
        Decimal,
        'Lax',
        'Python',
        condition='Allowed values: `Decimal(0), Decimal(1)`.',
        valid_examples=[Decimal(0), Decimal(1)],
        invalid_examples=[Decimal(2), Decimal(100)],
        core_schemas=[core_schema.BoolSchema],
    ),
    Row(
        bool,
        str,
        'Lax',
        'Python & JSON',
        condition=(
            "Allowed values: `'f'`, `'n'`, `'no'`, `'off'`, `'false'`, `'False'`, `'t'`, `'y'`, "
            "`'on'`, `'yes'`, `'true'`, `'True'`."
        ),
        valid_examples=['f', 'n', 'no', 'off', 'false', 'False', 't', 'y', 'on', 'yes', 'true', 'True'],
        invalid_examples=['test'],
        core_schemas=[core_schema.BoolSchema],
    ),
    Row(
        None,
        None,
        'Strict',
        'Python & JSON',
        core_schemas=[core_schema.NoneSchema],
    ),
    Row(
        date,
        date,
        'Strict',
        'Python',
        core_schemas=[core_schema.DateSchema],
    ),
    Row(
        date,
        datetime,
        'Lax',
        'Python',
        condition='Must be exact date, eg. no `H`, `M`, `S`, `f`.',
        valid_examples=[datetime(2017, 5, 5)],
        invalid_examples=[datetime(2017, 5, 5, 10)],
        core_schemas=[core_schema.DateSchema],
    ),
    Row(
        date,
        str,
        'Lax',
        'Python & JSON',
        condition='Format: `YYYY-MM-DD`.',
        valid_examples=['2017-05-05'],
        invalid_examples=['2017-5-5', '2017/05/05'],
        core_schemas=[core_schema.DateSchema],
    ),
    Row(
        date,
        bytes,
        'Lax',
        'Python',
        condition='Format: `YYYY-MM-DD` (UTF-8).',
        valid_examples=[b'2017-05-05'],
        invalid_examples=[b'2017-5-5', b'2017/05/05'],
        core_schemas=[core_schema.DateSchema],
    ),
    Row(
        date,
        int,
        'Lax',
        'Python & JSON',
        condition=(
            'Interpreted as seconds or ms from epoch. '
            'See [speedate](https://docs.rs/speedate/latest/speedate/). Must be exact date.'
        ),
        valid_examples=[1493942400000, 1493942400],
        invalid_examples=[1493942401000],
        core_schemas=[core_schema.DateSchema],
    ),
    Row(
        date,
        float,
        'Lax',
        'Python & JSON',
        condition=(
            'Interpreted as seconds or ms from epoch. '
            'See [speedate](https://docs.rs/speedate/latest/speedate/). Must be exact date.'
        ),
        valid_examples=[1493942400000.0, 1493942400.0],
        invalid_examples=[1493942401000.0],
        core_schemas=[core_schema.DateSchema],
    ),
    Row(
        date,
        Decimal,
        'Lax',
        'Python',
        condition=(
            'Interpreted as seconds or ms from epoch. '
            'See [speedate](https://docs.rs/speedate/latest/speedate/). Must be exact date.'
        ),
        valid_examples=[Decimal(1493942400000), Decimal(1493942400)],
        invalid_examples=[Decimal(1493942401000)],
        core_schemas=[core_schema.DateSchema],
    ),
    Row(
        datetime,
        datetime,
        'Strict',
        'Python',
        core_schemas=[core_schema.DatetimeSchema],
    ),
    Row(
        datetime,
        date,
        'Lax',
        'Python',
        valid_examples=[date(2017, 5, 5)],
        core_schemas=[core_schema.DatetimeSchema],
    ),
    Row(
        datetime,
        str,
        'Lax',
        'Python & JSON',
        condition='Format: `YYYY-MM-DDTHH:MM:SS.f`. See [speedate](https://docs.rs/speedate/latest/speedate/).',
        valid_examples=['2017-05-05 10:10:10', '2017-05-05T10:10:10.0002', '2017-05-05 10:10:10+00:00'],
        invalid_examples=['2017-5-5T10:10:10'],
        core_schemas=[core_schema.DatetimeSchema],
    ),
    Row(
        datetime,
        bytes,
        'Lax',
        'Python',
        condition=(
            'Format: `YYYY-MM-DDTHH:MM:SS.f`. See [speedate](https://docs.rs/speedate/latest/speedate/), (UTF-8).'
        ),
        valid_examples=[b'2017-05-05 10:10:10', b'2017-05-05T10:10:10.0002', b'2017-05-05 10:10:10+00:00'],
        invalid_examples=[b'2017-5-5T10:10:10'],
        core_schemas=[core_schema.DatetimeSchema],
    ),
    Row(
        datetime,
        int,
        'Lax',
        'Python & JSON',
        condition='Interpreted as seconds or ms from epoch, see [speedate](https://docs.rs/speedate/latest/speedate/).',
        valid_examples=[1493979010000, 1493979010],
        core_schemas=[core_schema.DatetimeSchema],
    ),
    Row(
        datetime,
        float,
        'Lax',
        'Python & JSON',
        condition='Interpreted as seconds or ms from epoch, see [speedate](https://docs.rs/speedate/latest/speedate/).',
        valid_examples=[1493979010000.0, 1493979010.0],
        core_schemas=[core_schema.DatetimeSchema],
    ),
    Row(
        datetime,
        Decimal,
        'Lax',
        'Python',
        condition='Interpreted as seconds or ms from epoch, see [speedate](https://docs.rs/speedate/latest/speedate/).',
        valid_examples=[Decimal(1493979010000), Decimal(1493979010)],
        core_schemas=[core_schema.DatetimeSchema],
    ),
    Row(
        time,
        time,
        'Strict',
        'Python',
        core_schemas=[core_schema.TimeSchema],
    ),
    Row(
        time,
        str,
        'Lax',
        'Python & JSON',
        condition='Format: `HH:MM:SS.FFFFFF`. See [speedate](https://docs.rs/speedate/latest/speedate/).',
        valid_examples=['10:10:10.0002'],
        invalid_examples=['1:1:1'],
        core_schemas=[core_schema.TimeSchema],
    ),
    Row(
        time,
        bytes,
        'Lax',
        'Python',
        condition='Format: `HH:MM:SS.FFFFFF`. See [speedate](https://docs.rs/speedate/latest/speedate/).',
        valid_examples=[b'10:10:10.0002'],
        invalid_examples=[b'1:1:1'],
        core_schemas=[core_schema.TimeSchema],
    ),
    Row(
        time,
        int,
        'Lax',
        'Python & JSON',
        condition='Interpreted as seconds, range `0 - 86399`.',
        valid_examples=[3720],
        invalid_examples=[-1, 86400],
        core_schemas=[core_schema.TimeSchema],
    ),
    Row(
        time,
        float,
        'Lax',
        'Python & JSON',
        condition='Interpreted as seconds, range `0 - 86399.9*`.',
        valid_examples=[3720.0002],
        invalid_examples=[-1.0, 86400.0],
        core_schemas=[core_schema.TimeSchema],
    ),
    Row(
        time,
        Decimal,
        'Lax',
        'Python',
        condition='Interpreted as seconds, range `0 - 86399.9*`.',
        valid_examples=[Decimal(3720.0002)],
        invalid_examples=[Decimal(-1), Decimal(86400)],
        core_schemas=[core_schema.TimeSchema],
    ),
    Row(
        timedelta,
        timedelta,
        'Strict',
        'Python',
        core_schemas=[core_schema.TimedeltaSchema],
    ),
    Row(
        timedelta,
        str,
        'Lax',
        'Python & JSON',
        condition='Format: `ISO8601`. See [speedate](https://docs.rs/speedate/latest/speedate/).',
        valid_examples=['1 days 10:10', '1 d 10:10'],
        invalid_examples=['1 10:10'],
        core_schemas=[core_schema.TimedeltaSchema],
    ),
    Row(
        timedelta,
        bytes,
        'Lax',
        'Python',
        condition='Format: `ISO8601`. See [speedate](https://docs.rs/speedate/latest/speedate/), (UTF-8).',
        valid_examples=[b'1 days 10:10', b'1 d 10:10'],
        invalid_examples=[b'1 10:10'],
        core_schemas=[core_schema.TimedeltaSchema],
    ),
    Row(
        timedelta,
        int,
        'Lax',
        'Python & JSON',
        condition='Interpreted as seconds.',
        valid_examples=[123_000],
        core_schemas=[core_schema.TimedeltaSchema],
    ),
    Row(
        timedelta,
        float,
        'Lax',
        'Python & JSON',
        condition='Interpreted as seconds.',
        valid_examples=[123_000.0002],
        core_schemas=[core_schema.TimedeltaSchema],
    ),
    Row(
        timedelta,
        Decimal,
        'Lax',
        'Python',
        condition='Interpreted as seconds.',
        valid_examples=[Decimal(123_000.0002)],
        core_schemas=[core_schema.TimedeltaSchema],
    ),
    Row(
        dict,
        dict,
        'Strict',
        'Python',
        core_schemas=[core_schema.DictSchema],
    ),
    Row(
        dict,
        'Object',
        'Strict',
        'JSON',
        valid_examples=['{"v": {"1": 1, "2": 2}}'],
        core_schemas=[core_schema.DictSchema],
    ),
    Row(
        dict,
        Mapping,
        'Lax',
        'Python',
        condition='Must implement the mapping interface and have an `items()` method.',
        valid_examples=[],
        core_schemas=[core_schema.DictSchema],
    ),
    Row(
        TypedDict,
        dict,
        'Strict',
        'Python',
        core_schemas=[core_schema.TypedDictSchema],
    ),
    Row(
        TypedDict,
        'Object',
        'Strict',
        'JSON',
        core_schemas=[core_schema.TypedDictSchema],
    ),
    Row(
        TypedDict,
        Any,
        'Strict',
        'Python',
        core_schemas=[core_schema.TypedDictSchema],
    ),
    Row(
        TypedDict,
        Mapping,
        'Lax',
        'Python',
        condition='Must implement the mapping interface and have an `items()` method.',
        valid_examples=[],
        core_schemas=[core_schema.TypedDictSchema],
    ),
    Row(
        list,
        list,
        'Strict',
        'Python',
        core_schemas=[core_schema.ListSchema],
    ),
    Row(
        list,
        'Array',
        'Strict',
        'JSON',
        core_schemas=[core_schema.ListSchema],
    ),
    Row(
        list,
        tuple,
        'Lax',
        'Python',
        core_schemas=[core_schema.ListSchema],
    ),
    Row(
        list,
        set,
        'Lax',
        'Python',
        core_schemas=[core_schema.ListSchema],
    ),
    Row(
        list,
        frozenset,
        'Lax',
        'Python',
        core_schemas=[core_schema.ListSchema],
    ),
    Row(
        list,
        deque,
        'Lax',
        'Python',
        core_schemas=[core_schema.ListSchema],
    ),
    Row(
        list,
        'dict_keys',
        'Lax',
        'Python',
        core_schemas=[core_schema.ListSchema],
    ),
    Row(
        list,
        'dict_values',
        'Lax',
        'Python',
        core_schemas=[core_schema.ListSchema],
    ),
    Row(
        tuple,
        tuple,
        'Strict',
        'Python',
        core_schemas=[core_schema.TuplePositionalSchema, core_schema.TupleVariableSchema],
    ),
    Row(
        tuple,
        'Array',
        'Strict',
        'JSON',
        core_schemas=[core_schema.TuplePositionalSchema, core_schema.TupleVariableSchema],
    ),
    Row(
        tuple,
        list,
        'Lax',
        'Python',
        core_schemas=[core_schema.TuplePositionalSchema, core_schema.TupleVariableSchema],
    ),
    Row(
        tuple,
        set,
        'Lax',
        'Python',
        core_schemas=[core_schema.TuplePositionalSchema, core_schema.TupleVariableSchema],
    ),
    Row(
        tuple,
        frozenset,
        'Lax',
        'Python',
        core_schemas=[core_schema.TuplePositionalSchema, core_schema.TupleVariableSchema],
    ),
    Row(
        tuple,
        deque,
        'Lax',
        'Python',
        core_schemas=[core_schema.TuplePositionalSchema, core_schema.TupleVariableSchema],
    ),
    Row(
        tuple,
        'dict_keys',
        'Lax',
        'Python',
        core_schemas=[core_schema.TuplePositionalSchema, core_schema.TupleVariableSchema],
    ),
    Row(
        tuple,
        'dict_values',
        'Lax',
        'Python',
        core_schemas=[core_schema.TuplePositionalSchema, core_schema.TupleVariableSchema],
    ),
    Row(
        set,
        set,
        'Strict',
        'Python',
        core_schemas=[core_schema.SetSchema],
    ),
    Row(
        set,
        'Array',
        'Strict',
        'JSON',
        core_schemas=[core_schema.SetSchema],
    ),
    Row(
        set,
        list,
        'Lax',
        'Python',
        core_schemas=[core_schema.SetSchema],
    ),
    Row(
        set,
        tuple,
        'Lax',
        'Python',
        core_schemas=[core_schema.SetSchema],
    ),
    Row(
        set,
        frozenset,
        'Lax',
        'Python',
        core_schemas=[core_schema.SetSchema],
    ),
    Row(
        set,
        deque,
        'Lax',
        'Python',
        core_schemas=[core_schema.SetSchema],
    ),
    Row(
        set,
        'dict_keys',
        'Lax',
        'Python',
        core_schemas=[core_schema.SetSchema],
    ),
    Row(
        set,
        'dict_values',
        'Lax',
        'Python',
        core_schemas=[core_schema.SetSchema],
    ),
    Row(
        frozenset,
        frozenset,
        'Strict',
        'Python',
        core_schemas=[core_schema.FrozenSetSchema],
    ),
    Row(
        frozenset,
        'Array',
        'Strict',
        'JSON',
        core_schemas=[core_schema.FrozenSetSchema],
    ),
    Row(
        frozenset,
        list,
        'Lax',
        'Python',
        core_schemas=[core_schema.FrozenSetSchema],
    ),
    Row(
        frozenset,
        tuple,
        'Lax',
        'Python',
        core_schemas=[core_schema.FrozenSetSchema],
    ),
    Row(
        frozenset,
        set,
        'Lax',
        'Python',
        core_schemas=[core_schema.FrozenSetSchema],
    ),
    Row(
        frozenset,
        deque,
        'Lax',
        'Python',
        core_schemas=[core_schema.FrozenSetSchema],
    ),
    Row(
        frozenset,
        'dict_keys',
        'Lax',
        'Python',
        core_schemas=[core_schema.FrozenSetSchema],
    ),
    Row(
        frozenset,
        'dict_values',
        'Lax',
        'Python',
        core_schemas=[core_schema.FrozenSetSchema],
    ),
    Row(
        isinstance,
        Any,
        'Strict',
        'Python',
        condition='`isinstance()` check returns `True`.',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        isinstance,
        '-',
        'Strict',
        'JSON',
        condition='Never valid.',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        callable,
        Any,
        'Strict',
        'Python',
        condition='`callable()` check returns `True`.',
        core_schemas=[core_schema.CallableSchema],
    ),
    Row(
        callable,
        '',
        'Strict',
        'JSON',
        condition='Never valid.',
        core_schemas=[core_schema.CallableSchema],
    ),
    Row(
        deque,
        deque,
        'Strict',
        'Python',
        core_schemas=[core_schema.WrapValidatorFunctionSchema],
    ),
    Row(
        deque,
        'Array',
        'Strict',
        'Json',
        core_schemas=[core_schema.WrapValidatorFunctionSchema],
    ),
    Row(
        deque,
        list,
        'Lax',
        'Python',
        core_schemas=[core_schema.ChainSchema],
    ),
    Row(
        deque,
        tuple,
        'Lax',
        'Python',
        core_schemas=[core_schema.ChainSchema],
    ),
    Row(
        deque,
        set,
        'Lax',
        'Python',
        core_schemas=[core_schema.ChainSchema],
    ),
    Row(
        deque,
        frozenset,
        'Lax',
        'Python',
        core_schemas=[core_schema.ChainSchema],
    ),
    Row(
        Any,
        Any,
        'Strict',
        'Python & JSON',
        core_schemas=[core_schema.AnySchema],
    ),
    Row(
        typing.NamedTuple,
        typing.NamedTuple,
        'Strict',
        'Python',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        typing.NamedTuple,
        'Array',
        'Strict',
        'JSON',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        typing.NamedTuple,
        collections.namedtuple,
        'Strict',
        'Python',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        typing.NamedTuple,
        tuple,
        'Strict',
        'Python',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        typing.NamedTuple,
        list,
        'Strict',
        'Python',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        typing.NamedTuple,
        dict,
        'Strict',
        'Python',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        collections.namedtuple,
        collections.namedtuple,
        'Strict',
        'Python',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        collections.namedtuple,
        'Array',
        'Strict',
        'JSON',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        collections.namedtuple,
        typing.NamedTuple,
        'Strict',
        'Python',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        collections.namedtuple,
        tuple,
        'Strict',
        'Python',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        collections.namedtuple,
        list,
        'Strict',
        'Python',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        collections.namedtuple,
        dict,
        'Strict',
        'Python',
        core_schemas=[core_schema.CallSchema],
    ),
    Row(
        Sequence,
        list,
        'Strict',
        'Python',
        core_schemas=[core_schema.ChainSchema],
    ),
    Row(
        Sequence,
        'Array',
        'Strict',
        'JSON',
        core_schemas=[core_schema.ChainSchema],
    ),
    Row(
        Sequence,
        tuple,
        'Lax',
        'Python',
        core_schemas=[core_schema.ChainSchema],
    ),
    Row(
        Sequence,
        deque,
        'Lax',
        'Python',
        core_schemas=[core_schema.ChainSchema],
    ),
    Row(
        Iterable,
        list,
        'Strict',
        'Python',
        core_schemas=[core_schema.GeneratorSchema],
    ),
    Row(
        Iterable,
        'Array',
        'Strict',
        'JSON',
        core_schemas=[core_schema.GeneratorSchema],
    ),
    Row(
        Iterable,
        tuple,
        'Strict',
        'Python',
        core_schemas=[core_schema.GeneratorSchema],
    ),
    Row(
        Iterable,
        set,
        'Strict',
        'Python',
        core_schemas=[core_schema.GeneratorSchema],
    ),
    Row(
        Iterable,
        frozenset,
        'Strict',
        'Python',
        core_schemas=[core_schema.GeneratorSchema],
    ),
    Row(
        Iterable,
        deque,
        'Strict',
        'Python',
        core_schemas=[core_schema.GeneratorSchema],
    ),
    Row(
        Type,
        Type,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsSubclassSchema],
    ),
    Row(
        Pattern,
        str,
        'Strict',
        'Python & JSON',
        condition='Input should be a valid pattern.',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        Pattern,
        bytes,
        'Strict',
        'Python',
        condition='Input should be a valid pattern.',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Address,
        IPv4Address,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        IPv4Address,
        IPv4Interface,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        IPv4Address,
        str,
        'Strict',
        'JSON',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        IPv4Address,
        str,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Address,
        bytes,
        'Lax',
        'Python',
        valid_examples=[b'\x00\x00\x00\x00'],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Address,
        int,
        'Lax',
        'Python',
        condition='integer representing the IP address, should be less than `2**32`',
        valid_examples=[168_430_090],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Interface,
        IPv4Interface,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        IPv4Interface,
        str,
        'Strict',
        'JSON',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        IPv4Interface,
        IPv4Address,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Interface,
        str,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Interface,
        bytes,
        'Lax',
        'Python',
        valid_examples=[b'\xff\xff\xff\xff'],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Interface,
        tuple,
        'Lax',
        'Python',
        valid_examples=[('192.168.0.1', '24')],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Interface,
        int,
        'Lax',
        'Python',
        condition='integer representing the IP address, should be less than `2**32`',
        valid_examples=[168_430_090],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Network,
        IPv4Network,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        IPv4Network,
        str,
        'Strict',
        'JSON',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        IPv4Network,
        IPv4Address,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Network,
        IPv4Interface,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Network,
        str,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Network,
        bytes,
        'Lax',
        'Python',
        valid_examples=[b'\xff\xff\xff\xff'],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv4Network,
        int,
        'Lax',
        'Python',
        condition='integer representing the IP network, should be less than `2**32`',
        valid_examples=[168_430_090],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Address,
        IPv6Address,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        IPv6Address,
        IPv6Interface,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        IPv6Address,
        str,
        'Strict',
        'JSON',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        IPv6Address,
        str,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Address,
        bytes,
        'Lax',
        'Python',
        valid_examples=[b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01'],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Address,
        int,
        'Lax',
        'Python',
        condition='integer representing the IP address, should be less than `2**128`',
        valid_examples=[340_282_366_920_938_463_463_374_607_431_768_211_455],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Interface,
        IPv6Interface,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        IPv6Interface,
        str,
        'Strict',
        'JSON',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        IPv6Interface,
        IPv6Address,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Interface,
        str,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Interface,
        bytes,
        'Lax',
        'Python',
        valid_examples=[b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01'],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Interface,
        tuple,
        'Lax',
        'Python',
        valid_examples=[('2001:db00::1', '120')],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Interface,
        int,
        'Lax',
        'Python',
        condition='integer representing the IP address, should be less than `2**128`',
        valid_examples=[340_282_366_920_938_463_463_374_607_431_768_211_455],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Network,
        IPv6Network,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        IPv6Network,
        str,
        'Strict',
        'JSON',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        IPv6Network,
        IPv6Address,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Network,
        IPv6Interface,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Network,
        str,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Network,
        bytes,
        'Lax',
        'Python',
        valid_examples=[b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01'],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IPv6Network,
        int,
        'Lax',
        'Python',
        condition='integer representing the IP address, should be less than `2**128`',
        valid_examples=[340_282_366_920_938_463_463_374_607_431_768_211_455],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        Enum,
        Enum,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        Enum,
        Any,
        'Strict',
        'JSON',
        condition='Input value should be convertible to enum values.',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        Enum,
        Any,
        'Lax',
        'Python',
        condition='Input value should be convertible to enum values.',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IntEnum,
        IntEnum,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        IntEnum,
        Any,
        'Strict',
        'JSON',
        condition='Input value should be convertible to enum values.',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        IntEnum,
        Any,
        'Lax',
        'Python',
        condition='Input value should be convertible to enum values.',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        Decimal,
        Decimal,
        'Strict',
        'Python',
        core_schemas=[core_schema.CustomErrorSchema],
    ),
    Row(
        Decimal,
        int,
        'Strict',
        'JSON',
        core_schemas=[core_schema.CustomErrorSchema],
    ),
    Row(
        Decimal,
        str,
        'Strict',
        'JSON',
        core_schemas=[core_schema.CustomErrorSchema],
    ),
    Row(
        Decimal,
        float,
        'Strict',
        'JSON',
        core_schemas=[core_schema.CustomErrorSchema],
    ),
    Row(
        Decimal,
        int,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        Decimal,
        str,
        'Lax',
        'Python & JSON',
        condition='Must match `[0-9]+(\\.[0-9]+)?`.',
        valid_examples=['3.141'],
        invalid_examples=['test', '3.141x'],
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        Decimal,
        float,
        'Lax',
        'Python & JSON',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        Path,
        Path,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        Path,
        str,
        'Strict',
        'JSON',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        Path,
        str,
        'Lax',
        'Python',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        UUID,
        UUID,
        'Strict',
        'Python',
        core_schemas=[core_schema.IsInstanceSchema],
    ),
    Row(
        UUID,
        str,
        'Strict',
        'JSON',
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        UUID,
        str,
        'Lax',
        'Python',
        valid_examples=['{12345678-1234-5678-1234-567812345678}'],
        core_schemas=[core_schema.AfterValidatorFunctionSchema],
    ),
    Row(
        ByteSize,
        str,
        'Strict',
        'Python & JSON',
        valid_examples=['1.2', '1.5 KB', '6.2EiB'],
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        ByteSize,
        int,
        'Strict',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        ByteSize,
        float,
        'Strict',
        'Python & JSON',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
    Row(
        ByteSize,
        Decimal,
        'Strict',
        'Python',
        core_schemas=[core_schema.PlainValidatorFunctionSchema],
    ),
]
