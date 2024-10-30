penalty_series = [0, 1, 3, 7, 15, 31, 63, 127, 255, 511]
SUM_PAY = 0


def up_to_next_penalty(num):
    for i, e, in enumerate(penalty_series):
        if e == num:
            return penalty_series[i + 1]


def add_penalty(books_cost: list):
    books = []
    for cost in books_cost:
        books.append([cost, 0])
    return books


def merging(target: list[int], sacrifice: list[int]):
    global SUM_PAY
    print("marge:", target[0], sacrifice[0])
    print("pay:", sacrifice[0], sacrifice[1], target[1])
    print("sum:", sacrifice[0] + sacrifice[1] + target[1])
    SUM_PAY += sacrifice[0] + sacrifice[1] + target[1]
    result = [target[0] + sacrifice[0], up_to_next_penalty(target[1])]
    print(SUM_PAY)
    return result


def get_expensive_book(books: list[list], penalty: int):
    expensive_book = [-1, penalty]
    for book in books:
        if book[0] > expensive_book[0] and book[1] == penalty:
            expensive_book = book[0], book[1]
    return list(expensive_book)


def get_cheapest_book(books: list[list], penalty: int):
    cheapest_book = [1000000, penalty]
    for book in books:
        if book[0] < cheapest_book[0] and book[1] == penalty:
            cheapest_book = book[0], book[1]
    return list(cheapest_book)


def best_boots_method_1(foo: list):
    to_enchant = list(foo)
    global SUM_PAY
    to_enchant.remove(2)
    to_enchant.sort(reverse=True)
    books = add_penalty(to_enchant)
    tool = [2, 0]
    while books:
        sum_penalty = 0
        for book in books:
            sum_penalty += book[1]
        if sum_penalty == 0:
            tool = merging(tool, books.pop(0))
            while sum(book[1] == 0 for book in books) >= 4:
                print("1")
                expensive_book = get_expensive_book(books, 0)
                cheapest_book = get_cheapest_book(books, 0)
                books.remove(list(expensive_book))
                books.remove(list(cheapest_book))
                new_marg_book = merging(expensive_book, cheapest_book)
                books.append(new_marg_book)
                cheapest_book = get_cheapest_book(books, 0)
                books.remove(list(cheapest_book))
                new_marg_book = merging(get_cheapest_book(books, 0), cheapest_book)
                books.remove(list(get_cheapest_book(books, 0)))
                books.append(new_marg_book)
            while sum(book[1] == 0 for book in books) >= 2:
                print("2")
                expensive_book = get_expensive_book(books, 0)
                cheapest_book = get_cheapest_book(books, 0)
                books.remove(list(expensive_book))
                books.remove(list(cheapest_book))
                new_marg_book = merging(expensive_book, cheapest_book)
                books.append(new_marg_book)
            books = sorted(books, key=lambda x: x[0], reverse=True)
            print(books)
            if books[-1][1] == 0:
                print("3")
                last_array = books.pop(-1)
                books.insert(0, last_array)

        elif sum_penalty >= 1:
            tool = merging(tool, books.pop(0))

    print(SUM_PAY)
    SUM_PAY = 0


def foo(arr: list[list]):
    find_penalty_0 = [array for array in arr if array[1] == 0]
    find_book_2 = [array for array in arr if array[0] == 2]
    if len(find_penalty_0) >= 2 and len(find_book_2) >= 1:
        return True


def best_boots_method_3(foo: list):
    to_enchant = list(foo)
    global SUM_PAY
    to_enchant.remove(2)
    to_enchant.sort(reverse=True)
    books = add_penalty(to_enchant)
    tool = [2, 0]
    while books:
        sum_penalty = 0
        for book in books:
            sum_penalty += book[1]
        if sum_penalty == 0:
            tool = merging(tool, books.pop(0))
            while (sum(book[1] == 0 for book in books) >= 2 and
                   any(book[0] == 2 for book in books if book[1] == 0)):
                for i in range(len(books)):
                    if books[i][0] == 2:
                        book_of_2 = books.pop(i)
                        expensive_book = get_expensive_book(books, 0)
                        books.remove(list(expensive_book))
                        new_marg_book = merging(expensive_book, book_of_2)
                        books.append(new_marg_book)
                        break

            while sum(book[1] == 0 for book in books) >= 2:
                expensive_book = get_expensive_book(books, 0)
                books.remove(list(expensive_book))
                new_marg_book = merging(expensive_book, get_expensive_book(books, 0))
                books.remove(list(get_expensive_book(books, 0)))
                books.append(new_marg_book)
            books = sorted(books, key=lambda x: x[0], reverse=True)

            if books[-1][1] == 0:
                last_array = books.pop(-1)
                books.insert(0, last_array)

        elif sum_penalty >= 1:
            tool = merging(tool, books.pop(0))

    print(SUM_PAY)
    SUM_PAY = 0


def most_expensive_first_method(to_enchant: list):
    to_enchant.remove(2)
    to_enchant.sort(reverse=True)
    books = add_penalty(to_enchant)
    tool = [2, 0]
    print(books)
    # while len(books) > 1:


sword1 = [2, 6, 6, 3, 5, 2, 4]
sword2 = [2, 3, 2, 6, 4, 2, 5, 6]



print("array:", sword1)
print(best_boots_method_1(sword1))
print()
print()
print(best_boots_method_3(sword1))
# print(add_penalty(ex))
# most_expensive_first_method(ex)
# print(merging([10, 0], [5, 0]))
