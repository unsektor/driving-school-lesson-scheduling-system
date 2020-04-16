import typing


def chunk(list_: list, chunk_count: int) -> typing.Iterator:
    """ Split list of items into sequence of chunk list by given chunks count keeping approximate equal same of each"""
    list_size = len(list_)
    chunk_size = int(list_size / chunk_count)  # equal to math.floor (round fraction down)

    for chunk_number in range(0, chunk_count):
        yield list_[chunk_number * chunk_size: (chunk_number + 1) * chunk_size]


def distribute(list_: list) -> typing.Iterator:
    """ Returns iterator over list going consistently from edges to center (from begin, from end, from begin, etc...)"""
    for index in range(0, len(list_)):
        if index % 2 == 0:
            yield list_[int(index / 2)]
            continue
        yield list_[-int((index + 1) / 2)]


def distribute2(list_: list, chunk_count: int) -> typing.Iterator:
    """
    Advanced distribution that wraps each list chunk with main distribution
    algorithm, switching direction (straight, reversed) by order (even, odd)
    """
    chunked_list = list(chunk(list_, chunk_count))
    distributed_chunk_number_list = distribute(list(range(0, chunk_count)))

    generator_list = []

    for index, chunk_number in enumerate(distributed_chunk_number_list):
        chunk_item_list = chunked_list[chunk_number]

        if index % 2 != 0:
            chunk_item_list = reversed(chunk_item_list)

        generator_list.append(distribute(list(chunk_item_list)))

    finished_set = set()

    generator_list_len = len(generator_list)

    while len(finished_set) != generator_list_len:
        for generator in generator_list:
            if generator in finished_set:
                continue
            try:
                yield next(generator)
            except StopIteration:
                finished_set.add(generator)
