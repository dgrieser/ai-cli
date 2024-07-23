from miniaudio import StreamableSource
import queue
import time
from io import RawIOBase

class ByteQueueFile(RawIOBase, StreamableSource):

    def __init__(self):
        super().__init__()
        self._queue = queue.Queue()
        self._position = 0
        self._done = False

    def read(self, size=-1) -> bytes:
        if self._done and self._queue.empty():
            return bytes()

        while self._queue.empty():
            time.sleep(0.1)

        next = None
        while next is None:
            next = self._queue.get(block=True, timeout=0.1)
            if self._done and next is None:
                next = bytes()
                break

        self._position += len(next)
        return next

    def readinto(self, bytes) -> int | None:
        next = self.read()
        if next is None:
            return None

        if len(bytes) < len(next):
            raise ValueError("Buffer is too small, expected exactly " + str(len(next)) + " bytes, but got " + str(len(bytes)))

        bytes[:len(next)] = next
        return len(next)

    def readall(self) -> bytes:
        result = bytearray()
        while True:
            next = self.read()
            if next is None or len(next) == 0:
                break
            result.extend(next)
        return result

    def write(self, data) -> int:
        self._queue.put(data)
        return len(data)

    @property
    def seekable(self) -> bool:
        return False

    def seek(self, offset, whence=0):
        pass

    def tell(self) -> int:
        return self._position

    def close(self) -> None:
        self._done = True

    @property
    def closed(self) -> bool:
        return self._done

    def fileno(self) -> int:
        return super().fileno()

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        return False

    def readable(self) -> bool:
        return True

    def readlines(self, hint: int = -1) -> list[bytes]:
        raise NotImplementedError()

    def readline(self, size: int | None = -1) -> bytes:
        raise NotImplementedError()

    def truncate(self, size: int | None = ...) -> int:
        raise NotImplementedError()

    def writable(self) -> bool:
        return True

    def writelines(self, lines) -> None:
        raise NotImplementedError()

    def __str__(self):
        return 'Audio Stream'

    def __repr__(self):
        return 'ByteQueueFile()'

    def __del__(self) -> None:
        return self.close()