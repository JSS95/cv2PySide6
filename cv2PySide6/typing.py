from numpy.typing import NDArray
from PySide6.QtCore import Signal
from typing import Protocol, Callable, Any

__all__ = [
    'ArrayProcessorProtocol',
]


class ArrayProcessorProtocol(Protocol):
    """
    Type annotation for array processor protocol.

    New image array is passed down from upstream pipeline to
    ``setArray`` slot. ``arrayChanged`` emits processed array.
    """
    setArray: Callable[['ArrayProcessorProtocol', NDArray], Any]
    arrayChanged: Signal
