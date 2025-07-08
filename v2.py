from typing import Iterator


class V2[T]:
    def __init__(self, x: T, y: T) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"V2[{self.x}, {self.y}]"

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, o):
        return V2(self.x + o.x, self.y + o.y)

    def __mul__(self, n):
        return V2(self.x * n, self.y * n)

    def __sub__(self, o):
        return self + (o * -1)

    def __truediv__(self, n):
        return V2(self.x / n, self.y / n)

    def __floordiv__(self, n):
        return V2(self.x // n, self.y // n)

    def dist(self, o) -> float:
        """
        distance between 2 points
        """
        return ((self.x - o.x) ** 2 + (self.y - o.y) ** 2) ** 0.5

    def dot(self, o) -> float:
        """
        calculate dot product between itself and a given vector
        """
        return self.x * o.x + self.y * o.y

    def mag(self) -> float:
        """
        returns magnitude of the vector
        """
        return self.dist(V2(0, 0))

    def norm(self):
        """
        returns normalized vector
        """
        return self / self.mag()

    def __eq__(self, o) -> bool:
        return self.x == o.x and self.y == o.y

    def __iter__(self) -> Iterator[T]:
        return iter([self.x, self.y])

    def __getitem__(self, key: int) -> T:
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise KeyError(f"index {key} out of range")
