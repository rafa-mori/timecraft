import copy
from calendar import c
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Set,
    Tuple,
    TypeVar,
    Union,
)

T = TypeVar("T")


class ChainableMeta(type):
    """Metaclasse para registrar comportamentos dinâmicos."""

    _behavior_registry: Dict[str, Callable] = {}

    @classmethod
    def register_behavior(cls, name: str, behavior: Callable):
        """Registra um novo comportamento dinâmico."""
        cls._behavior_registry[name] = behavior

    def __getattr__(cls, name: str):
        """Permite acesso a comportamentos registrados."""
        if name in cls._behavior_registry:
            return cls._behavior_registry[name]
        raise AttributeError(f"Comportamento '{name}' não registrado")


class ChainableBase(Generic[T]):
    """Classe base para todos os comportamentos encadeáveis."""

    _value: T

    def __init__(self, value: T):
        self._value = value

    def __call__(self, next_value: Any) -> "ChainableBase":
        """Comportamento padrão de chamada."""
        return self.__class__(self._value + next_value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value!r})"

    def then(self, func: Callable[[T], Any]) -> "ChainableBase":
        """
        Aplica uma função ao valor e retorna um novo ChainableBase.
        Permite encadeamento de operações adicionais.
        """
        return self.__class__(func(self._value))


class ChainableWrapper(ChainableBase[T], metaclass=ChainableMeta):
    """
    Classe que permite encadear chamadas de métodos e operadores para vários tipos diferentes,
    onde cada operação retorna um novo ChainableWrapper com o valor atualizado.

    Esta classe foi projetada para atuar como um wrapper flexível para valores,
    permitindo a construção de pipelines de operações encadeadas, semelhante
    ao conceito de APIs fluentes. Ela é útil para manipulação dinâmica de dados,
    processamento em cadeia e construção de pequenas DSLs (Domain Specific Languages) internas.

    Principais Características:
    - **Encadeamento de Operações**: Cada operação retorna uma nova instância de ChainableWrapper,
        permitindo chamadas sequenciais.
    - **Polimorfismo de Operadores**: Sobrecarga de operadores comuns (+, -, *, ==, etc.)
        para funcionar com diversos tipos de dados subjacentes.
    - **Segurança de Tipo Reforçada**: Verificações de tipo em tempo de execução para
        operações específicas e mensagens de erro claras.
    - **Imutabilidade Opcional**: A maioria das operações retorna uma nova instância,
        preservando o estado anterior, útil para pipelines de dados.
    - **Métodos para Casos de Uso Comuns**: Inclusão de métodos como `apply`, `filter`, `map`,
        `merge`, que são fundamentais em cenários de transformação de dados.

    Tipos de dados suportados para operações (quando aplicável):
    - int, float, complex: Operações aritméticas e comparações.
    - str: Concatenação, comparações, acesso a caracteres.
    - dict: União (merge), acesso por chave, iteração.
    - list, tuple: Concatenação, acesso por índice, iteração, filtragem, mapeamento.
    - set: União, interseção, diferença.

    Exemplos de uso:
    >>> runner = g(5)
    >>> result = runner + 10
    >>> print(result)  # Saída: ChainableWrapper(15)
    >>> result = g(5) + "hello"
    >>> print(result)  # Saída: ChainableWrapper('5hello')
    >>> result = g([1, 2]) + [3, 4]
    >>> print(result)  # Saída: ChainableWrapper([1, 2, 3, 4])
    >>> result = g({"a": 1}) + {"b": 2}
    >>> print(result)  # Saída: ChainableWrapper({'a': 1, 'b': 2})
    >>> # Para o desafio original:
    >>> # g(12)(5)(8)(1)(3) == 29
    >>> # Assumindo que __call__ adiciona:
    >>> print(g(12)(5)(8)(1)(3) == 29) # Saída: True
    >>>
    >>> # Exemplo de uso com métodos mais avançados:
    >>> data = g([1, 2, 3, 4, 5])
    >>> transformed_data = data.filter(lambda x: x % 2 == 0).map(lambda x: x * 10)
    >>> print(transformed_data.value) # Saída: [20, 40]
    >>>
    >>> config = g({"debug": False, "port": 8080})
    >>> updated_config = config.merge({"port": 9000, "env": "production"})
    >>> print(updated_config.value) # Saída: {'debug': False, 'port': 9000, 'env': 'production'}
    """

    _value: Any  # Internamente, o valor atual que está sendo manipulado
    _iterator: Iterator[Any]  # Para gerenciar a iteração em __next__

    def __init__(self, current_value: Any):
        """
        Inicializa o ChainableWrapper com um valor inicial.
        """
        self._value = current_value
        self._iterator = iter([])  # Inicializa um iterador vazio

    ## <editor-fold default="collapsed" desc="Métodos especiais de representação e hash">

    def __str__(self) -> str:
        """
        Retorna a representação string do valor interno.
        """
        try:
            return str(self._value)
        except Exception as e:
            return f"Erro ao converter para string: {e}"

    def __repr__(self) -> str:
        """
        Retorna a representação oficial do ChainableWrapper.
        """
        return f"ChainableWrapper({self._value!r})"

    def __hash__(self) -> int:
        """
        Retorna o hash do valor interno, se possível.
        """
        return hash(self._value)

    ## </editor-fold>

    ## <editor-fold default="collapsed" desc="Métodos especiais de conversão (tentam converter)">

    def to_bool(self) -> bool:
        """
        Tenta converter o valor interno para booleano.
        """
        return bool(self._value)

    def to_int(self) -> int:
        """
        Tenta converter o valor interno para inteiro.
        """
        try:
            return int(self._value)
        except (ValueError, TypeError) as e:
            raise TypeError(
                f"Não foi possível converter '{self._value!r}' para inteiro: {e}"
            )

    def to_float(self) -> float:
        """
        Tenta converter o valor interno para float.
        """
        try:
            return float(self._value)
        except (ValueError, TypeError) as e:
            raise TypeError(
                f"Não foi possível converter '{self._value!r}' para float: {e}"
            )

    def to_complex(self) -> complex:
        """
        Tenta converter o valor interno para complexo.
        """
        try:
            return complex(self._value)
        except (ValueError, TypeError) as e:
            raise TypeError(
                f"Não foi possível converter '{self._value!r}' para complexo: {e}"
            )

    def to_dict(self) -> Dict[Any, Any]:
        """
        Tenta converter o valor interno para dicionário.
        Retorna o dicionário diretamente (não um ChainableWrapper).
        """
        if isinstance(self._value, dict):
            return self._value
        raise TypeError(
            f"O objeto {type(self._value)} não pode ser convertido para dicionário diretamente."
        )

    def to_list(self) -> List[Any]:
        """
        Tenta converter o valor interno para lista.
        Retorna a lista diretamente (não um ChainableWrapper).
        """
        try:
            return list(self._value)
        except TypeError as e:
            raise TypeError(
                f"Não foi possível converter '{self._value!r}' para lista: {e}"
            )

    def to_tuple(self) -> Tuple[Any, ...]:
        """
        Tenta converter o valor interno para tupla.
        Retorna a tupla diretamente (não um ChainableWrapper).
        """
        try:
            return tuple(self._value)
        except TypeError as e:
            raise TypeError(
                f"Não foi possível converter '{self._value!r}' para tupla: {e}"
            )

    def to_set(self) -> Set[Any]:
        """
        Tenta converter o valor interno para conjunto.
        Retorna o conjunto diretamente (não um ChainableWrapper).
        """
        try:
            return set(self._value)
        except TypeError as e:
            raise TypeError(
                f"Não foi possível converter '{self._value!r}' para conjunto: {e}"
            )

    @property
    def value(self) -> Any:
        """
        Retorna o valor subjacente atual do ChainableWrapper.
        """
        return self._value

    ## </editor-fold>

    ## <editor-fold default="collapsed" desc="Métodos de Operações Encadeadas (Fluentes)">

    def apply(self, func: Callable[[Any], Any]) -> "ChainableWrapper":
        """
        Aplica uma função ao valor atual e retorna um novo ChainableWrapper
        com o resultado.
        Exemplo: g(5).apply(lambda x: x * 2) -> ChainableWrapper(10)
        """
        try:
            new_value = func(self._value)
            return ChainableWrapper(new_value)
        except Exception as e:
            raise TypeError(f"Falha ao aplicar função ao valor {self._value!r}: {e}")

    def filter(self, predicate: Callable[[Any], bool]) -> "ChainableWrapper":
        """
        Filtra os elementos do valor atual (se for uma coleção iterável)
        usando a função de predicado fornecida. Retorna um novo ChainableWrapper
        com os elementos filtrados.
        Exemplo: g([1, 2, 3, 4]).filter(lambda x: x % 2 == 0) -> ChainableWrapper([2, 4])
        """
        if not hasattr(self._value, "__iter__"):
            raise TypeError(
                f"O objeto {type(self._value)} não é iterável para filtragem."
            )
        try:
            filtered_elements = [item for item in self._value if predicate(item)]
            return ChainableWrapper(
                type(self._value)(filtered_elements)
            )  # Mantém o tipo da coleção
        except Exception as e:
            raise TypeError(f"Falha ao filtrar valor {self._value!r}: {e}")

    def map(self, mapper: Callable[[Any], Any]) -> "ChainableWrapper":
        """
        Mapeia os elementos do valor atual (se for uma coleção iterável)
        aplicando a função mapper a cada um. Retorna um novo ChainableWrapper
        com os elementos mapeados.
        Exemplo: g([1, 2, 3]).map(lambda x: x * 2) -> ChainableWrapper([2, 4, 6])
        """
        if not hasattr(self._value, "__iter__"):
            raise TypeError(
                f"O objeto {type(self._value)} não é iterável para mapeamento."
            )
        try:
            mapped_elements = [mapper(item) for item in self._value]
            return ChainableWrapper(
                type(self._value)(mapped_elements)
            )  # Mantém o tipo da coleção
        except Exception as e:
            raise TypeError(f"Falha ao mapear valor {self._value!r}: {e}")

    def merge(self, other: Any) -> "ChainableWrapper":
        """
        Realiza uma operação de merge com outro valor.
        - Para dicionários: une os dicionários (valores do 'other' sobrescrevem).
        - Para listas/tuplas: concatena.
        - Para conjuntos: une os conjuntos.
        - Outros tipos: tenta adição.
        Retorna um novo ChainableWrapper com o resultado do merge.
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other

        if isinstance(self._value, dict) and isinstance(other_value, dict):
            return ChainableWrapper({**self._value, **other_value})
        elif isinstance(self._value, list) and isinstance(other_value, list):
            return ChainableWrapper(self._value + other_value)
        elif isinstance(self._value, tuple) and isinstance(other_value, tuple):
            return ChainableWrapper(
                self._value + other_value
            )  # Tuplas são imutáveis, '+' cria nova
        elif isinstance(self._value, set) and isinstance(other_value, set):
            return ChainableWrapper(self._value.union(other_value))
        else:
            # Tenta operação padrão de adição se os tipos não forem coleções para merge específico
            return self.__add__(other_value)

    def flatten(self) -> "ChainableWrapper":
        """
        Achata uma coleção aninhada (lista de listas, tupla de tuplas, etc.) em uma única coleção.
        Suporta apenas coleções de coleções.
        Exemplo: g([[1, 2], [3, 4]]).flatten() -> ChainableWrapper([1, 2, 3, 4])
        """
        if not isinstance(self._value, (list, tuple)):
            raise TypeError(
                f"Flatten só suporta listas ou tuplas de listas/tuplas. Tipo atual: {type(self._value)}"
            )

        flat_list = []
        for item in self._value:
            if isinstance(item, (list, tuple)):
                flat_list.extend(item)
            else:
                flat_list.append(item)  # Adiciona itens não-coleções diretamente
        return ChainableWrapper(
            type(self._value)(flat_list)
        )  # Mantém o tipo original da coleção

    ## </editor-fold>

    ## <editor-fold default="collapsed" desc="Métodos especiais de operações e comparação (Sobrecargas de operadores)">

    def __call__(self, next_value: Any) -> "ChainableWrapper":
        """
        Permite chamar a instância como uma função, realizando uma adição por padrão.
        Isso replica o comportamento de encadeamento do desafio original (g(12)(5)...).
        """
        try:
            # Tenta realizar uma adição. Cuidado com tipos não-numéricos aqui se a intenção é estritamente numérica.
            return ChainableWrapper(self._value + next_value)
        except TypeError:
            raise TypeError(
                f"A chamada direta como função (__call__) não suporta a operação de adição entre {type(self._value)} e {type(next_value)}."
            )

    def __add__(self, other: Any) -> "ChainableWrapper":
        """
        Sobrecarga do operador de adição (+).
        Suporta adição entre números, concatenação de strings,
        união de dicionários (merge), e concatenação de listas/tuplas.
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other

        # Lógica para tipos compatíveis com adição nativa
        if isinstance(self._value, (int, float, complex)) and isinstance(
            other_value, (int, float, complex)
        ):
            return ChainableWrapper(self._value + other_value)
        elif isinstance(self._value, str) and isinstance(other_value, str):
            return ChainableWrapper(self._value + other_value)
        elif isinstance(self._value, list) and isinstance(other_value, list):
            return ChainableWrapper(self._value + other_value)
        elif isinstance(self._value, tuple) and isinstance(other_value, tuple):
            return ChainableWrapper(self._value + other_value)
        elif isinstance(self._value, set) and isinstance(other_value, set):
            return ChainableWrapper(self._value.union(other_value))
        elif isinstance(self._value, dict) and isinstance(other_value, dict):
            # Para dicionários, o operador + não é nativo. Usamos merge explícito para clareza.
            return ChainableWrapper({**self._value, **other_value})
        else:
            raise TypeError(
                f"Operação de adição não suportada entre {type(self._value)} e {type(other_value)}."
            )

    def __sub__(self, other: Any) -> "ChainableWrapper":
        """
        Sobrecarga do operador de subtração (-).
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other
        try:
            return ChainableWrapper(self._value - other_value)
        except TypeError as e:
            raise TypeError(
                f"Operação de subtração não suportada entre {type(self._value)} e {type(other_value)}: {e}"
            )

    def __mul__(self, other: Any) -> "ChainableWrapper":
        """
        Sobrecarga do operador de multiplicação (*).
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other
        try:
            return ChainableWrapper(self._value * other_value)
        except TypeError as e:
            raise TypeError(
                f"Operação de multiplicação não suportada entre {type(self._value)} e {type(other_value)}: {e}"
            )

    def __truediv__(self, other: Any) -> "ChainableWrapper":
        """
        Sobrecarga do operador de divisão real (/).
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other
        if other_value == 0:
            raise ZeroDivisionError("Divisão por zero não é permitida.")
        try:
            return ChainableWrapper(self._value / other_value)
        except TypeError as e:
            raise TypeError(
                f"Operação de divisão não suportada entre {type(self._value)} e {type(other_value)}: {e}"
            )

    def __floordiv__(self, other: Any) -> "ChainableWrapper":
        """
        Sobrecarga do operador de divisão inteira (//).
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other
        if other_value == 0:
            raise ZeroDivisionError("Divisão por zero não é permitida.")
        try:
            return ChainableWrapper(self._value // other_value)
        except TypeError as e:
            raise TypeError(
                f"Operação de divisão inteira não suportada entre {type(self._value)} e {type(other_value)}: {e}"
            )

    def __mod__(self, other: Any) -> "ChainableWrapper":
        """
        Sobrecarga do operador de módulo (%).
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other
        if other_value == 0:
            raise ZeroDivisionError("Operação de módulo por zero não é permitida.")
        try:
            return ChainableWrapper(self._value % other_value)
        except TypeError as e:
            raise TypeError(
                f"Operação de módulo não suportada entre {type(self._value)} e {type(other_value)}: {e}"
            )

    def __pow__(self, other: Any) -> "ChainableWrapper":
        """
        Sobrecarga do operador de exponenciação (**).
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other
        try:
            return ChainableWrapper(self._value**other_value)
        except TypeError as e:
            raise TypeError(
                f"Operação de exponenciação não suportada entre {type(self._value)} e {type(other_value)}: {e}"
            )

    def __eq__(self, other: Any) -> bool:
        """
        Sobrecarga do operador de igualdade (==).
        Compara o valor interno com outro objeto ou com o valor interno de outro ChainableWrapper.
        """
        if isinstance(other, ChainableWrapper):
            return self._value == other._value
        return self._value == other

    def __ne__(self, other: Any) -> bool:
        """
        Sobrecarga do operador de diferença (!=).
        """
        return not self.__eq__(other)

    def _compare(self, other: Any, op_func: Callable[[Any, Any], bool]) -> bool:
        """Função auxiliar para métodos de comparação."""
        other_value = other._value if isinstance(other, ChainableWrapper) else other
        try:
            return op_func(self._value, other_value)
        except TypeError as e:
            raise TypeError(
                f"Comparação não suportada entre {type(self._value)} e {type(other_value)}: {e}"
            )

    def __lt__(self, other: Any) -> bool:
        """Sobrecarga do operador menor que (<)."""
        return self._compare(other, lambda a, b: a < b)

    def __le__(self, other: Any) -> bool:
        """Sobrecarga do operador menor ou igual a (<=)."""
        return self._compare(other, lambda a, b: a <= b)

    def __gt__(self, other: Any) -> bool:
        """Sobrecarga do operador maior que (>)."""
        return self._compare(other, lambda a, b: a > b)

    def __ge__(self, other: Any) -> bool:
        """Sobrecarga do operador maior ou igual a (>=)."""
        return self._compare(other, lambda a, b: a >= b)

    def __len__(self) -> int:
        """
        Retorna o comprimento do valor interno, se suportado.
        """
        try:
            return len(self._value)
        except TypeError as e:
            raise TypeError(
                f"O objeto {type(self._value)} não tem comprimento definido: {e}"
            )

    def __getitem__(self, key: Any) -> "ChainableWrapper":
        """
        Permite acesso a itens por índice ou chave, se suportado pelo valor interno.
        Retorna um novo ChainableWrapper com o item acessado.
        """
        try:
            return ChainableWrapper(self._value[key])
        except (TypeError, KeyError) as e:
            raise TypeError(f"O objeto {type(self._value)} não suporta indexação: {e}")

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Permite atribuição de itens por índice ou chave, se suportado.
        Modifica o valor interno diretamente.
        """
        try:
            self._value[key] = value
        except (TypeError, KeyError) as e:
            raise TypeError(
                f"O objeto {type(self._value)} não suporta atribuição de itens: {e}"
            )

    def __delitem__(self, key: Any) -> None:
        """
        Permite deleção de itens por índice ou chave, se suportado.
        Modifica o valor interno diretamente.
        """
        try:
            del self._value[key]
        except (TypeError, KeyError) as e:
            raise TypeError(
                f"O objeto {type(self._value)} não suporta deleção de itens: {e}"
            )

    def __contains__(self, item: Any) -> bool:
        """
        Verifica se um item está contido no valor interno, se suportado.
        """
        try:
            return item in self._value
        except TypeError as e:
            raise TypeError(
                f"O objeto {type(self._value)} não suporta verificação de pertencimento: {e}"
            )

    def __iter__(self) -> Iterator[Any]:
        """
        Retorna um iterador para o valor interno.
        """
        try:
            self._iterator = iter(self._value)
            return self
        except TypeError as e:
            raise TypeError(f"O objeto {type(self._value)} não é iterável: {e}")

    def __next__(self) -> Any:
        """
        Retorna o próximo item da iteração.
        """
        return next(self._iterator)

    def __and__(self, other: Any) -> "ChainableWrapper":
        """
        Sobrecarga do operador AND (&).
        Para números (int, bool): bitwise AND. Para sets: interseção.
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other

        if isinstance(self._value, (int, bool)) and isinstance(
            other_value, (int, bool)
        ):
            return ChainableWrapper(self._value & other_value)
        elif isinstance(self._value, set) and isinstance(other_value, set):
            return ChainableWrapper(self._value.intersection(other_value))
        else:
            raise TypeError(
                f"Operação AND (&) não suportada entre {type(self._value)} e {type(other_value)}."
            )

    def __or__(self, other: Any) -> "ChainableWrapper":
        """
        Sobrecarga do operador OR (|).
        Para números (int, bool): bitwise OR. Para sets: união.
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other

        if isinstance(self._value, (int, bool)) and isinstance(
            other_value, (int, bool)
        ):
            return ChainableWrapper(self._value | other_value)
        elif isinstance(self._value, set) and isinstance(other_value, set):
            return ChainableWrapper(self._value.union(other_value))
        else:
            raise TypeError(
                f"Operação OR (|) não suportada entre {type(self._value)} e {type(other_value)}."
            )

    def __xor__(self, other: Any) -> "ChainableWrapper":
        """
        Sobrecarga do operador XOR (^).
        Para números (int, bool): bitwise XOR. Para sets: diferença simétrica.
        """
        other_value = other._value if isinstance(other, ChainableWrapper) else other

        if isinstance(self._value, (int, bool)) and isinstance(
            other_value, (int, bool)
        ):
            return ChainableWrapper(self._value ^ other_value)
        elif isinstance(self._value, set) and isinstance(other_value, set):
            return ChainableWrapper(self._value.symmetric_difference(other_value))
        else:
            raise TypeError(
                f"Operação XOR (^) não suportada entre {type(self._value)} e {type(other_value)}."
            )

    # Método especial para encadeamento flexível
    def then(self, func: Callable[[T], Any]) -> "ChainableWrapper":
        """Aplica uma função ao valor e retorna novo ChainableWrapper."""
        return ChainableWrapper(func(self._value))

    ## </editor-fold>


# Decorator para adicionar comportamentos dinamicamente
def chainable_behavior(
    name: str = "None",
) -> Callable[
    [Callable[[ChainableBase], ChainableBase]], Callable[[ChainableBase], ChainableBase]
]:
    """Decorator para registrar novos comportamentos."""

    def decorator(func):
        behavior_name = name or func.__name__
        ChainableMeta.register_behavior(behavior_name, func)
        return func

    return decorator


# <editor-fold desc="Exemplos de Comportamentos Dinâmicos">


# Exemplo de uso com comportamentos dinâmicos
@chainable_behavior("add_five")
def add_five(chainable: ChainableBase) -> ChainableBase:
    return chainable.then(lambda x: x + 5)


@chainable_behavior("square")
def square(chainable: ChainableBase) -> ChainableBase:
    return chainable.then(lambda x: x * x)


# </editor-fold>


def run(initial_value: Any) -> "ChainableWrapper":
    """
    Função de inicialização alternativa para criar uma instância de ChainableWrapper.
    Permite o encadeamento de operações a partir de um valor inicial.
    Exemplo de uso: chainable(5) cria um ChainableWrapper com o valor 5.
    """

    class ChainableWrapperInitializer(ChainableWrapper):
        """
        Classe interna para inicializar o ChainableWrapper com um valor inicial.
        Permite o uso de run(5) para criar uma instância de ChainableWrapper.
        """

        def __call__(self, next_value: Any) -> "ChainableWrapper":
            """
            Permite encadear chamadas como run(5)(10)(15), retornando um novo ChainableWrapper.
            """
            return ChainableWrapperInitializer(self._value + next_value)

    return ChainableWrapperInitializer(initial_value)


def main():
    """
    Função principal para testes e demonstrações.
    Pode ser usada para executar exemplos de uso do ChainableWrapper.
    """
    # Exemplo simples de uso
    runner = run(5)
    result = runner + 10
    print(result)  # Saída: ChainableWrapper(15)

    # Exemplo de encadeamento
    result = run(5)(10).then(lambda x: x * 2).value()
    print(result)  # Saída: 30

    # Exemplo de uso com métodos encadeados
    result = run(5)(5).value().square()  # (5+5)^2 = 100
    print(result)  # ChainableWrapper(100)


if __name__ == "__main__":
    # Executa a função principal se o script for executado diretamente
    # Isso permite testes rápidos e demonstrações.
    main()

# end of file
