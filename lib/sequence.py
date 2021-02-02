import typing


def chunk(list_: list, chunk_count: int) -> typing.Iterator:
    """ Split list of items into sequence of chunk list by given chunks count keeping approximate equal same of each"""
    list_size = len(list_)
    chunk_size = int(list_size / chunk_count)  # equal to `math.floor` (round fraction down)

    for chunk_number in range(chunk_count-1):
        yield list_[chunk_number * chunk_size: (chunk_number + 1) * chunk_size]
    yield list_[(chunk_count-1) * chunk_size:]

    # FIXME !!! `chunk(['1', 3])` -> `[[],[],[]]`


def tapering_spiral(  # AKA dist1
        list_: list,
        confirmation_callable: typing.Optional[typing.Callable[[typing.Any], bool]] = None
) -> typing.Iterator:
    """ Returns iterator over list going consistently from edges to center (from begin, from end, from begin, etc...)"""
    if confirmation_callable is None:
        for index in range(0, len(list_)):
            if index % 2 == 0:
                yield list_[int(index / 2)]
                continue
            yield list_[-int((index + 1) / 2)]
        return

    direction = 0  # 0 = straight (forward), 1 = reverse (backward)
    forward_position = 0  # from the beginning
    backward_position = 0  # from the end
    count = 0
    total = len(list_)

    while count != total:
        if direction == 0:
            item = list_[forward_position]
            forward_position += 1
            assert forward_position < len(list_)

            if confirmation_callable(item):
                yield item
                count += 1
                direction = 1
            continue

        if direction == 1:
            item = list_[(-backward_position)-1]

            backward_position += 1

            if confirmation_callable(item):
                yield item
                count += 1
                direction = 0
            continue


def distribute2(list_: list, chunk_count: int) -> typing.Iterator:
    """
    Advanced distribution that wraps each list chunk with main distribution
    algorithm, switching direction (straight, reversed) by order (even, odd)
    """
    chunked_list = list(chunk(list_, chunk_count))
    distributed_chunk_number_list = tapering_spiral(list(range(0, chunk_count)))

    generator_list = []

    for index, chunk_number in enumerate(distributed_chunk_number_list):
        chunk_item_list = chunked_list[chunk_number]

        if index % 2 != 0:
            chunk_item_list = reversed(chunk_item_list)

        generator_list.append(tapering_spiral(list(chunk_item_list)))

    finished_set = set()

    generator_list_len = len(generator_list)

    x = {}

    while len(finished_set) != generator_list_len:
        for i, generator in enumerate(generator_list):
            if i not in x:
                x[i] = []

            if generator in finished_set:
                continue
            try:
                item = next(generator)

                x[i].append(item)

                yield item
            except StopIteration as e:
                e = e
                finished_set.add(generator)



if __name__ == '__main__':
    print(list(distribute2([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], chunk_count=3)))
