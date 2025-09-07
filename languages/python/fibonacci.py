def fibonacci_generator():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def fibonacci_list(n):
    result = []
    fib_gen = fibonacci_generator()
    for _ in range(n):
        result.append(next(fib_gen))
    return result

def fibonacci_nth(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

if __name__ == "__main__":
    print("Generatore di numeri di Fibonacci")
    print("-" * 35)
    
    print("\nPrimi 10 numeri di Fibonacci:")
    print(fibonacci_list(10))
    
    print("\nGeneratore infinito (primi 15 numeri):")
    fib_gen = fibonacci_generator()
    for i in range(15):
        print(f"F({i}) = {next(fib_gen)}")
    
    print(f"\nIl 20° numero di Fibonacci è: {fibonacci_nth(20)}")
    
    n = int(input("\nInserisci quanti numeri di Fibonacci vuoi vedere: "))
    print(f"\nPrimi {n} numeri di Fibonacci:")
    print(fibonacci_list(n))