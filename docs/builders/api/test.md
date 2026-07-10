Attribute: AGAIN = 1
Attribute: ASCEND = 2
Attribute: NEXT = 3

<a id="thirdparty.pparse.lib.EndOfDataException"></a>

--------------------------------------------------------------
### EndOfDataException
--------------------------------------------------------------

```python
class EndOfDataException(Exception)
```
Raised when the end of the data currently available is reached.

<a id="thirdparty.pparse.lib.EndOfNodeException"></a>

--------------------------------------------------------------
### EndOfNodeException
--------------------------------------------------------------

```python
class EndOfNodeException(Exception)
```
Raised when the parser has finished processing the current node.

<a id="thirdparty.pparse.lib.UnsupportedFormatException"></a>

--------------------------------------------------------------
### UnsupportedFormatException
--------------------------------------------------------------

```python
class UnsupportedFormatException(Exception)
```
Raised when the observed data is not recognized by the parser.

<a id="thirdparty.pparse.lib.BufferFullException"></a>

--------------------------------------------------------------
### BufferFullException
--------------------------------------------------------------

```python
class BufferFullException(Exception)
```
Raised when a buffer cannot accept additional data.

<a id="thirdparty.pparse.lib.NodeContext"></a>

--------------------------------------------------------------
### NodeContext
--------------------------------------------------------------

```python
class NodeContext()
```
Holds the parser state and reader position associated with a single ``Node``.

``NodeContext`` is the glue between a ``Node`` and its ``Parser``.  It
owns the parser's state stack for the node and provides pass-through
reader methods so that parser state objects do not need a direct
reference to the underlying ``Reader``. It's also an all in one reference
to cut once parsing is complete and we need to restore memory.

Args:
    parent: The parent ``Node``, or ``None`` for the root.
    reader: The ``Reader`` positioned at the start of this node's data.
    parser: The ``Parser`` responsible for interpreting this node.

#### Attributes

| Attribute    | Default      |
| ------------ | ------------ |
| _reader      | reader.dup() |
| _state_stack | []           |
| _parent      | parent       |
| _start       | self.tell()  |
| _end         | None         |
| _parser      | parser       |
| _descendants | []           |

#### Functions

| Prototype                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------- |
| def [`__init__`](#thirdparty.pparse.lib.NodeContext.__init__)``(parent: Optional[Node], reader: Reader, parser: Parser) -> None |
| def [`parent`](#thirdparty.pparse.lib.NodeContext.parent)``() -> Optional[Node]                                                 |
| def [`parent_ctx`](#thirdparty.pparse.lib.NodeContext.parent_ctx)``() -> Optional[NodeContext]                                  |
| def [`reader`](#thirdparty.pparse.lib.NodeContext.reader)``() -> Reader                                                         |
| def [`parser`](#thirdparty.pparse.lib.NodeContext.parser)``() -> Parser                                                         |
| def [`_init_state`](#thirdparty.pparse.lib.NodeContext._init_state)``(state: Type[Any]) -> None                                 |
| def [`_init_states`](#thirdparty.pparse.lib.NodeContext._init_states)``(states: List[Type[Any]]) -> None                        |
| def [`_next_state`](#thirdparty.pparse.lib.NodeContext._next_state)``(state: Type[Any]) -> None                                 |
| def [`_next_states`](#thirdparty.pparse.lib.NodeContext._next_states)``(states: List[Type[Any]]) -> None                        |
| def [`state`](#thirdparty.pparse.lib.NodeContext.state)``() -> Any                                                              |
| def [`_pop_state`](#thirdparty.pparse.lib.NodeContext._pop_state)``() -> Any                                                    |
| def [`set_remaining`](#thirdparty.pparse.lib.NodeContext.set_remaining)``(length: int) -> None                                  |
| def [`mark_end`](#thirdparty.pparse.lib.NodeContext.mark_end)``(node: Node) -> None                                             |
| def [`mark_field_start`](#thirdparty.pparse.lib.NodeContext.mark_field_start)``() -> None                                       |
| def [`field_start`](#thirdparty.pparse.lib.NodeContext.field_start)``() -> int                                                  |
| def [`dup`](#thirdparty.pparse.lib.NodeContext.dup)``() -> Reader                                                               |
| def [`tell`](#thirdparty.pparse.lib.NodeContext.tell)``() -> int                                                                |
| def [`seek`](#thirdparty.pparse.lib.NodeContext.seek)``(*args: Any = (), **kwargs: Any = {}) -> Any                             |
| def [`skip`](#thirdparty.pparse.lib.NodeContext.skip)``(*args: Any = (), **kwargs: Any = {}) -> Any                             |
| def [`peek`](#thirdparty.pparse.lib.NodeContext.peek)``(*args: Any = (), **kwargs: Any = {}) -> bytes                           |
| def [`read`](#thirdparty.pparse.lib.NodeContext.read)``(*args: Any = (), **kwargs: Any = {}) -> bytes                           |
| def [`left`](#thirdparty.pparse.lib.NodeContext.left)``() -> int                                                                |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.__init__"></a>

#### def [`__init__`](#thirdparty.pparse.lib.NodeContext.__init__)``(parent: Optional[Node], reader: Reader, parser: Parser) -> None
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.parent"></a>

#### def [`parent`](#thirdparty.pparse.lib.NodeContext.parent)``() -> Optional[Node]
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.parent_ctx"></a>

#### def [`parent_ctx`](#thirdparty.pparse.lib.NodeContext.parent_ctx)``() -> Optional[NodeContext]
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.reader"></a>

#### def [`reader`](#thirdparty.pparse.lib.NodeContext.reader)``() -> Reader
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.parser"></a>

#### def [`parser`](#thirdparty.pparse.lib.NodeContext.parser)``() -> Parser
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext._init_state"></a>

#### def [`_init_state`](#thirdparty.pparse.lib.NodeContext._init_state)``(state: Type[Any]) -> None
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext._init_states"></a>

#### def [`_init_states`](#thirdparty.pparse.lib.NodeContext._init_states)``(states: List[Type[Any]]) -> None
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext._next_state"></a>

#### def [`_next_state`](#thirdparty.pparse.lib.NodeContext._next_state)``(state: Type[Any]) -> None
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext._next_states"></a>

#### def [`_next_states`](#thirdparty.pparse.lib.NodeContext._next_states)``(states: List[Type[Any]]) -> None
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.state"></a>

#### def [`state`](#thirdparty.pparse.lib.NodeContext.state)``() -> Any
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext._pop_state"></a>

#### def [`_pop_state`](#thirdparty.pparse.lib.NodeContext._pop_state)``() -> Any
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.set_remaining"></a>

#### def [`set_remaining`](#thirdparty.pparse.lib.NodeContext.set_remaining)``(length: int) -> None
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.mark_end"></a>

#### def [`mark_end`](#thirdparty.pparse.lib.NodeContext.mark_end)``(node: Node) -> None
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.mark_field_start"></a>

#### def [`mark_field_start`](#thirdparty.pparse.lib.NodeContext.mark_field_start)``() -> None
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.field_start"></a>

#### def [`field_start`](#thirdparty.pparse.lib.NodeContext.field_start)``() -> int
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.dup"></a>

#### def [`dup`](#thirdparty.pparse.lib.NodeContext.dup)``() -> Reader
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.tell"></a>

#### def [`tell`](#thirdparty.pparse.lib.NodeContext.tell)``() -> int
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.seek"></a>

#### def [`seek`](#thirdparty.pparse.lib.NodeContext.seek)``(*args: Any = (), **kwargs: Any = {}) -> Any
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.skip"></a>

#### def [`skip`](#thirdparty.pparse.lib.NodeContext.skip)``(*args: Any = (), **kwargs: Any = {}) -> Any
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.peek"></a>

#### def [`peek`](#thirdparty.pparse.lib.NodeContext.peek)``(*args: Any = (), **kwargs: Any = {}) -> bytes
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.read"></a>

#### def [`read`](#thirdparty.pparse.lib.NodeContext.read)``(*args: Any = (), **kwargs: Any = {}) -> bytes
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.NodeContext.left"></a>

#### def [`left`](#thirdparty.pparse.lib.NodeContext.left)``() -> int
Return bytes remaining between the current position and the range end.

The internal reader must be a ``Range`` for this to work.
- **Returns:**
  - int - Number of bytes remaining in the range.
- **Raises:**
  - Exception - If the internal reader is not a ``Range``.
Attribute: UNLOADED_VALUE = UnloadedValue()

<a id="thirdparty.pparse.lib.RecursionControl"></a>

--------------------------------------------------------------
### RecursionControl
--------------------------------------------------------------

```python
class RecursionControl()
```
Configurable guard that limits how deeply ``Node.load`` recurses.

``RecursionControl`` is passed to ``Node.load`` to give callers
fine-grained control over which parts of the parse tree are eagerly
expanded.  At each node, ``stopped`` is called to decide whether
recursion should halt.

Args:
    min_depth: Nodes at depths below this value are always loaded,
        ignoring ``max_depth`` and the callback.
    max_depth: Nodes at depths above this value are never loaded.
    callback: An optional callable that receives a ``Node`` and returns
        ``True`` to stop recursion at that node.  Only called when
        ``min_depth <= cur_depth <= max_depth``.

#### Attributes

| Attribute      | Default             |
| -------------- | ------------------- |
| MAX_DEPTH      | 9223372036854775807 |
| cur_depth      | 0                   |
| max_seen_depth | 0                   |
| min_depth      | min_depth           |
| max_depth      | max_depth           |
| cb             | callback            |

#### Functions

| Prototype                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| def [`__init__`](#thirdparty.pparse.lib.RecursionControl.__init__)``(min_depth: int = 0, max_depth: int = MAX_DEPTH, callback: Optional[Callable[[Node], bool]] = None) -> None |
| def [`stopped`](#thirdparty.pparse.lib.RecursionControl.stopped)``(node: Node) -> bool                                                                                          |
| def [`increase_depth`](#thirdparty.pparse.lib.RecursionControl.increase_depth)``(amount: int = 1) -> None                                                                       |
| def [`decrease_depth`](#thirdparty.pparse.lib.RecursionControl.decrease_depth)``(amount: int = 1) -> None                                                                       |
| def [`current_depth`](#thirdparty.pparse.lib.RecursionControl.current_depth)``() -> int                                                                                         |
| def [`deepest_depth`](#thirdparty.pparse.lib.RecursionControl.deepest_depth)``() -> int                                                                                         |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.RecursionControl.__init__"></a>

#### def [`__init__`](#thirdparty.pparse.lib.RecursionControl.__init__)``(min_depth: int = 0, max_depth: int = MAX_DEPTH, callback: Optional[Callable[[Node], bool]] = None) -> None
Return the maximum recursion depth seen since this instance was created.
- **Returns:**
  - int - The high-water mark for recursion depth.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.RecursionControl.stopped"></a>

#### def [`stopped`](#thirdparty.pparse.lib.RecursionControl.stopped)``(node: Node) -> bool
Return the maximum recursion depth seen since this instance was created.
- **Returns:**
  - int - The high-water mark for recursion depth.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.RecursionControl.increase_depth"></a>

#### def [`increase_depth`](#thirdparty.pparse.lib.RecursionControl.increase_depth)``(amount: int = 1) -> None
Return the maximum recursion depth seen since this instance was created.
- **Returns:**
  - int - The high-water mark for recursion depth.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.RecursionControl.decrease_depth"></a>

#### def [`decrease_depth`](#thirdparty.pparse.lib.RecursionControl.decrease_depth)``(amount: int = 1) -> None
Return the maximum recursion depth seen since this instance was created.
- **Returns:**
  - int - The high-water mark for recursion depth.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.RecursionControl.current_depth"></a>

#### def [`current_depth`](#thirdparty.pparse.lib.RecursionControl.current_depth)``() -> int
Return the maximum recursion depth seen since this instance was created.
- **Returns:**
  - int - The high-water mark for recursion depth.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.RecursionControl.deepest_depth"></a>

#### def [`deepest_depth`](#thirdparty.pparse.lib.RecursionControl.deepest_depth)``() -> int
Return the maximum recursion depth seen since this instance was created.
- **Returns:**
  - int - The high-water mark for recursion depth.

<a id="thirdparty.pparse.lib.Node"></a>

--------------------------------------------------------------
### Node
--------------------------------------------------------------

```python
class Node()
```
A single node in the pparse parse-tree.

A ``Node`` represents a region of binary data that a ``Parser`` knows about
and _possibly_ how to interpret.  Its ``_value`` starts as ``UNLOADED_VALUE`` and is
populated lazily on first access via the ``value`` property, which
triggers ``load()``.

Each node owns a ``NodeContext`` that carries the parser's state machine (for the Node)
and a ``Reader`` positioned at the start of the node's data offset.

Args:
    reader: A ``Reader`` positioned at the start of this node's data.
    parser: The ``Parser`` responsible for interpreting this node.
    default_value: Initial value; defaults to ``UNLOADED_VALUE`` so that
        the node is parsed lazily on first access.
    parent: The parent ``Node``, or ``None`` for the root.
    ctx_class: An optional ``NodeContext`` subclass to instantiate instead
        of the default ``NodeContext``.
    ctx_args: Extra keyword arguments forwarded to ``ctx_class``.

#### Attributes

| Attribute | Default |
| --------- | ------- |
| value     | None    |

#### Functions

| Prototype                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------- |
| def [`clear_ctx`](#thirdparty.pparse.lib.Node.clear_ctx)``() -> Node                                             |
| def [`ctx`](#thirdparty.pparse.lib.Node.ctx)``() -> NodeContext                                                  |
| def [`dump`](#thirdparty.pparse.lib.Node.dump)``(depth: int = 0, step: int = 2, dumper: Any = None) -> None      |
| def [`from_xml`](#thirdparty.pparse.lib.Node.from_xml)``(src_xml: Any, ctx_ref: Any) -> Optional[Node]           |
| def [`length`](#thirdparty.pparse.lib.Node.length)``() -> int                                                    |
| def [`load`](#thirdparty.pparse.lib.Node.load)``(recursion: Optional[RecursionControl] = None) -> Optional[Node] |
| def [`set_length`](#thirdparty.pparse.lib.Node.set_length)``(length: int) -> Node                                |
| def [`tell`](#thirdparty.pparse.lib.Node.tell)``() -> int                                                        |
| def [`unload`](#thirdparty.pparse.lib.Node.unload)``() -> None                                                   |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Node.clear_ctx"></a>

#### def [`clear_ctx`](#thirdparty.pparse.lib.Node.clear_ctx)``() -> Node
Return the parsed value, triggering ``load()`` if not yet parsed.
- **Returns:**
  - Any - The node's parsed value (dict, list, scalar, or nested ``Node``).

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Node.ctx"></a>

#### def [`ctx`](#thirdparty.pparse.lib.Node.ctx)``() -> NodeContext
Return the parsed value, triggering ``load()`` if not yet parsed.
- **Returns:**
  - Any - The node's parsed value (dict, list, scalar, or nested ``Node``).

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Node.dump"></a>

#### def [`dump`](#thirdparty.pparse.lib.Node.dump)``(depth: int = 0, step: int = 2, dumper: Any = None) -> None
Return the parsed value, triggering ``load()`` if not yet parsed.
- **Returns:**
  - Any - The node's parsed value (dict, list, scalar, or nested ``Node``).

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Node.from_xml"></a>

#### def [`from_xml`](#thirdparty.pparse.lib.Node.from_xml)``(src_xml: Any, ctx_ref: Any) -> Optional[Node]
Return the parsed value, triggering ``load()`` if not yet parsed.
- **Returns:**
  - Any - The node's parsed value (dict, list, scalar, or nested ``Node``).

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Node.length"></a>

#### def [`length`](#thirdparty.pparse.lib.Node.length)``() -> int
Return the parsed value, triggering ``load()`` if not yet parsed.
- **Returns:**
  - Any - The node's parsed value (dict, list, scalar, or nested ``Node``).

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Node.load"></a>

#### def [`load`](#thirdparty.pparse.lib.Node.load)``(recursion: Optional[RecursionControl] = None) -> Optional[Node]
Return the parsed value, triggering ``load()`` if not yet parsed.
- **Returns:**
  - Any - The node's parsed value (dict, list, scalar, or nested ``Node``).

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Node.set_length"></a>

#### def [`set_length`](#thirdparty.pparse.lib.Node.set_length)``(length: int) -> Node
Return the parsed value, triggering ``load()`` if not yet parsed.
- **Returns:**
  - Any - The node's parsed value (dict, list, scalar, or nested ``Node``).

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Node.tell"></a>

#### def [`tell`](#thirdparty.pparse.lib.Node.tell)``() -> int
Return the parsed value, triggering ``load()`` if not yet parsed.
- **Returns:**
  - Any - The node's parsed value (dict, list, scalar, or nested ``Node``).

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Node.unload"></a>

#### def [`unload`](#thirdparty.pparse.lib.Node.unload)``() -> None
Return the parsed value, triggering ``load()`` if not yet parsed.
- **Returns:**
  - Any - The node's parsed value (dict, list, scalar, or nested ``Node``).

<a id="thirdparty.pparse.lib.Reader"></a>

--------------------------------------------------------------
### Reader
--------------------------------------------------------------

```python
class Reader()
```
Abstract interface for objects that provide sequential and random access to binary data.

Both ``Cursor`` and ``Range`` implement this interface.  Callers should
program to ``Reader`` wherever possible so that either concrete type can
be substituted transparently.

#### Functions

| Prototype                                                                |
| ------------------------------------------------------------------------ |
| def [`dup`](#thirdparty.pparse.lib.Reader.dup)``() -> Reader             |
| def [`tell`](#thirdparty.pparse.lib.Reader.tell)``() -> int              |
| def [`seek`](#thirdparty.pparse.lib.Reader.seek)``(offset: int) -> Any   |
| def [`skip`](#thirdparty.pparse.lib.Reader.skip)``(length: int) -> Any   |
| def [`peek`](#thirdparty.pparse.lib.Reader.peek)``(length: int) -> bytes |
| def [`read`](#thirdparty.pparse.lib.Reader.read)``(length: int) -> bytes |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Reader.dup"></a>

#### def [`dup`](#thirdparty.pparse.lib.Reader.dup)``() -> Reader
Read ``length`` bytes and advance the read position accordingly.
- **Parameters:**
  - int - Number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Reader.tell"></a>

#### def [`tell`](#thirdparty.pparse.lib.Reader.tell)``() -> int
Read ``length`` bytes and advance the read position accordingly.
- **Parameters:**
  - int - Number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Reader.seek"></a>

#### def [`seek`](#thirdparty.pparse.lib.Reader.seek)``(offset: int) -> Any
Read ``length`` bytes and advance the read position accordingly.
- **Parameters:**
  - int - Number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Reader.skip"></a>

#### def [`skip`](#thirdparty.pparse.lib.Reader.skip)``(length: int) -> Any
Read ``length`` bytes and advance the read position accordingly.
- **Parameters:**
  - int - Number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Reader.peek"></a>

#### def [`peek`](#thirdparty.pparse.lib.Reader.peek)``(length: int) -> bytes
Read ``length`` bytes and advance the read position accordingly.
- **Parameters:**
  - int - Number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Reader.read"></a>

#### def [`read`](#thirdparty.pparse.lib.Reader.read)``(length: int) -> bytes
Read ``length`` bytes and advance the read position accordingly.
- **Parameters:**
  - int - Number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

<a id="thirdparty.pparse.lib.Cursor"></a>

--------------------------------------------------------------
### Cursor
--------------------------------------------------------------

```python
class Cursor(Reader)
```
A stateful read pointer into a ``Data`` object.

``Cursor`` tracks the current byte offset and uses ``Data`` backend
for all I/O access.  It does not enforce any boundary; that
responsibility belongs to ``Range``.

Args:
    data: The backing ``Data`` object that performs actual I/O.
    offset: Initial byte offset within ``data``.

#### Attributes

| Attribute | Default |
| --------- | ------- |
| _data     | data    |
| _offset   | offset  |

#### Functions

| Prototype                                                                                      |
| ---------------------------------------------------------------------------------------------- |
| def [`__init__`](#thirdparty.pparse.lib.Cursor.__init__)``(data: Any, offset: int = 0) -> None |
| def [`cursor`](#thirdparty.pparse.lib.Cursor.cursor)``() -> Cursor                             |
| def [`dup`](#thirdparty.pparse.lib.Cursor.dup)``() -> Cursor                                   |
| def [`tell`](#thirdparty.pparse.lib.Cursor.tell)``() -> int                                    |
| def [`seek`](#thirdparty.pparse.lib.Cursor.seek)``(offset: int) -> Any                         |
| def [`skip`](#thirdparty.pparse.lib.Cursor.skip)``(length: int) -> Any                         |
| def [`peek`](#thirdparty.pparse.lib.Cursor.peek)``(length: int) -> bytes                       |
| def [`read`](#thirdparty.pparse.lib.Cursor.read)``(length: int, mode: Any = None) -> bytes     |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Cursor.__init__"></a>

#### def [`__init__`](#thirdparty.pparse.lib.Cursor.__init__)``(data: Any, offset: int = 0) -> None
Read ``length`` bytes.
- **Parameters:**
  - int - Max number of bytes to read.
  - Any - Optional read mode hint passed to the backing data source.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Cursor.cursor"></a>

#### def [`cursor`](#thirdparty.pparse.lib.Cursor.cursor)``() -> Cursor
Read ``length`` bytes.
- **Parameters:**
  - int - Max number of bytes to read.
  - Any - Optional read mode hint passed to the backing data source.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Cursor.dup"></a>

#### def [`dup`](#thirdparty.pparse.lib.Cursor.dup)``() -> Cursor
Read ``length`` bytes.
- **Parameters:**
  - int - Max number of bytes to read.
  - Any - Optional read mode hint passed to the backing data source.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Cursor.tell"></a>

#### def [`tell`](#thirdparty.pparse.lib.Cursor.tell)``() -> int
Read ``length`` bytes.
- **Parameters:**
  - int - Max number of bytes to read.
  - Any - Optional read mode hint passed to the backing data source.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Cursor.seek"></a>

#### def [`seek`](#thirdparty.pparse.lib.Cursor.seek)``(offset: int) -> Any
Read ``length`` bytes.
- **Parameters:**
  - int - Max number of bytes to read.
  - Any - Optional read mode hint passed to the backing data source.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Cursor.skip"></a>

#### def [`skip`](#thirdparty.pparse.lib.Cursor.skip)``(length: int) -> Any
Read ``length`` bytes.
- **Parameters:**
  - int - Max number of bytes to read.
  - Any - Optional read mode hint passed to the backing data source.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Cursor.peek"></a>

#### def [`peek`](#thirdparty.pparse.lib.Cursor.peek)``(length: int) -> bytes
Read ``length`` bytes.
- **Parameters:**
  - int - Max number of bytes to read.
  - Any - Optional read mode hint passed to the backing data source.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Cursor.read"></a>

#### def [`read`](#thirdparty.pparse.lib.Cursor.read)``(length: int, mode: Any = None) -> bytes
Read ``length`` bytes.
- **Parameters:**
  - int - Max number of bytes to read.
  - Any - Optional read mode hint passed to the backing data source.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

<a id="thirdparty.pparse.lib.Range"></a>

--------------------------------------------------------------
### Range
--------------------------------------------------------------

```python
class Range(Reader)
```
A bounded view over a region of a data source.

``Range`` wraps a ``Cursor`` and clamps all seek, skip, peek, and read
operations to the half-open interval ``[start, start + length]``.  It
does not duplicate any I/O logic — all actual data access is delegated
to the underlying cursor.

Args:
    cursor: A ``Cursor`` whose current position marks the start of the range.
    length: Number of bytes in the range.  Must be >= 0.
    offset: If >= 0, the initial read position within the range; otherwise
        defaults to the start of the range.

Raises:
    ValueError: If ``length`` is negative.

#### Attributes

| Attribute     | Default      |
| ------------- | ------------ |
| _start_cursor | cursor.dup() |

#### Functions

| Prototype                                                                                                             |
| --------------------------------------------------------------------------------------------------------------------- |
| def [`__init__`](#thirdparty.pparse.lib.Range.__init__)``(cursor: Cursor, length: int, offset: int = -1) -> None      |
| def [`_init`](#thirdparty.pparse.lib.Range._init)``(start_offset: int, length: int, current_offset: int = -1) -> None |
| def [`cursor`](#thirdparty.pparse.lib.Range.cursor)``() -> Cursor                                                     |
| def [`dup`](#thirdparty.pparse.lib.Range.dup)``() -> Range                                                            |
| def [`truncate`](#thirdparty.pparse.lib.Range.truncate)``(new_length: int) -> Range                                   |
| def [`length`](#thirdparty.pparse.lib.Range.length)``() -> int                                                        |
| def [`left`](#thirdparty.pparse.lib.Range.left)``() -> int                                                            |
| def [`valid_offset`](#thirdparty.pparse.lib.Range.valid_offset)``(offset: int) -> bool                                |
| def [`tell`](#thirdparty.pparse.lib.Range.tell)``() -> int                                                            |
| def [`seek`](#thirdparty.pparse.lib.Range.seek)``(offset: int) -> int                                                 |
| def [`_adjust_length`](#thirdparty.pparse.lib.Range._adjust_length)``(length: int) -> int                             |
| def [`skip`](#thirdparty.pparse.lib.Range.skip)``(length: int) -> Any                                                 |
| def [`peek`](#thirdparty.pparse.lib.Range.peek)``(length: int) -> bytes                                               |
| def [`read`](#thirdparty.pparse.lib.Range.read)``(length: int) -> bytes                                               |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.__init__"></a>

#### def [`__init__`](#thirdparty.pparse.lib.Range.__init__)``(cursor: Cursor, length: int, offset: int = -1) -> None
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range._init"></a>

#### def [`_init`](#thirdparty.pparse.lib.Range._init)``(start_offset: int, length: int, current_offset: int = -1) -> None
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.cursor"></a>

#### def [`cursor`](#thirdparty.pparse.lib.Range.cursor)``() -> Cursor
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.dup"></a>

#### def [`dup`](#thirdparty.pparse.lib.Range.dup)``() -> Range
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.truncate"></a>

#### def [`truncate`](#thirdparty.pparse.lib.Range.truncate)``(new_length: int) -> Range
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.length"></a>

#### def [`length`](#thirdparty.pparse.lib.Range.length)``() -> int
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.left"></a>

#### def [`left`](#thirdparty.pparse.lib.Range.left)``() -> int
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.valid_offset"></a>

#### def [`valid_offset`](#thirdparty.pparse.lib.Range.valid_offset)``(offset: int) -> bool
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.tell"></a>

#### def [`tell`](#thirdparty.pparse.lib.Range.tell)``() -> int
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.seek"></a>

#### def [`seek`](#thirdparty.pparse.lib.Range.seek)``(offset: int) -> int
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range._adjust_length"></a>

#### def [`_adjust_length`](#thirdparty.pparse.lib.Range._adjust_length)``(length: int) -> int
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.skip"></a>

#### def [`skip`](#thirdparty.pparse.lib.Range.skip)``(length: int) -> Any
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.peek"></a>

#### def [`peek`](#thirdparty.pparse.lib.Range.peek)``(length: int) -> bytes
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Range.read"></a>

#### def [`read`](#thirdparty.pparse.lib.Range.read)``(length: int) -> bytes
Read up to ``length`` bytes.

The byte count is clamped so it does not exceed the range boundary.
- **Parameters:**
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

<a id="thirdparty.pparse.lib.Data"></a>

--------------------------------------------------------------
### Data
--------------------------------------------------------------

```python
class Data()
```
Abstract data backend that provides I/O operations to ``Cursor`` objects.

``Data`` subclasses own the access to persistent storage (file, HTTP URL, mmap,
in-memory ``BytesIO``).  ``Data`` implements ``peek`` for non-advancing reads;
seek and read are provided with default implementations built on top of
``peek``.

The design keeps offset tracking out of ``Data``: a ``Cursor`` manages
the current position and passes itself to ``Data`` methods as a handle. A
``Cursor`` is not unlike a user-space defined file descriptor.

#### Functions

| Prototype                                                                              |
| -------------------------------------------------------------------------------------- |
| def [`open`](#thirdparty.pparse.lib.Data.open)``(offset: int = 0) -> Cursor            |
| def [`peek`](#thirdparty.pparse.lib.Data.peek)``(cursor: Cursor, length: int) -> bytes |
| def [`seek`](#thirdparty.pparse.lib.Data.seek)``(cursor: Cursor) -> int                |
| def [`read`](#thirdparty.pparse.lib.Data.read)``(cursor: Cursor, length: int) -> bytes |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Data.open"></a>

#### def [`open`](#thirdparty.pparse.lib.Data.open)``(offset: int = 0) -> Cursor
Read ``length`` bytes.

The base implementation uses ``peek``.  Subclasses that can perform a more
efficient read-and-seek in a single syscall should override ``read``.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Data.peek"></a>

#### def [`peek`](#thirdparty.pparse.lib.Data.peek)``(cursor: Cursor, length: int) -> bytes
Read ``length`` bytes.

The base implementation uses ``peek``.  Subclasses that can perform a more
efficient read-and-seek in a single syscall should override ``read``.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Data.seek"></a>

#### def [`seek`](#thirdparty.pparse.lib.Data.seek)``(cursor: Cursor) -> int
Read ``length`` bytes.

The base implementation uses ``peek``.  Subclasses that can perform a more
efficient read-and-seek in a single syscall should override ``read``.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Data.read"></a>

#### def [`read`](#thirdparty.pparse.lib.Data.read)``(cursor: Cursor, length: int) -> bytes
Read ``length`` bytes.

The base implementation uses ``peek``.  Subclasses that can perform a more
efficient read-and-seek in a single syscall should override ``read``.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

<a id="thirdparty.pparse.lib.HttpCachedData"></a>

--------------------------------------------------------------
### HttpCachedData
--------------------------------------------------------------

```python
class HttpCachedData(Data)
```
``Data`` backend that fetches remote content via HTTP with a local chunk cache.

Downloads the target resource in fixed-size chunks and keeps a bounded
LRU-style cache in memory.  Supports servers that advertise
``Accept-Ranges: bytes``; falls back to a "download from beginning" when Range
requests are not available.

Args:
    url: The full HTTP/HTTPS URL of the target resource.
    chunk_size: Size of each cache chunk in bytes. (Ideally close to page size or hardware cache size)
    chunk_max_count: Maximum number of chunks to keep in the cache (consider SDRAM available to process).
    session: An optional ``requests.Session`` to use for HTTP calls.
        A new session is created when this is ``None``.

Raises:
    Exception: If Range requests are not supported and the file is larger
        than the total cache capacity.

#### Attributes

| Attribute        | Default                                                                                               |
| ---------------- | ----------------------------------------------------------------------------------------------------- |
| CHUNK_SIZE       | 4096 * 256                                                                                            |
| MAX_CHUNKS       | 1024                                                                                                  |
| _session         | session                                                                                               |
| length           | int(response.headers['Content-Length'])                                                               |
| _supports_ranges | response.headers.get('Accept-Ranges', 'none').lower() == 'bytes'                                      |
| httpdata         | _HttpCachedData(url, chunk_size=chunk_size, chunk_max_count=chunk_max_count, session=(self._session)) |

#### Functions

| Prototype                                                                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| def [`__init__`](#thirdparty.pparse.lib.HttpCachedData.__init__)``(url: str, chunk_size: int = CHUNK_SIZE, chunk_max_count: int = MAX_CHUNKS, session: Optional[Any] = None) -> None |
| def [`peek`](#thirdparty.pparse.lib.HttpCachedData.peek)``(cursor: Cursor, length: int) -> bytes                                                                                     |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.HttpCachedData.__init__"></a>

#### def [`__init__`](#thirdparty.pparse.lib.HttpCachedData.__init__)``(url: str, chunk_size: int = CHUNK_SIZE, chunk_max_count: int = MAX_CHUNKS, session: Optional[Any] = None) -> None
Read ``length`` bytes at the cursor's position via the chunk cache.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.HttpCachedData.peek"></a>

#### def [`peek`](#thirdparty.pparse.lib.HttpCachedData.peek)``(cursor: Cursor, length: int) -> bytes
Read ``length`` bytes at the cursor's position via the chunk cache.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.
<!-- ALIAS: HttpRangeData is thirdparty.pparse.lib.data.HttpRangeData -->

<a id="thirdparty.pparse.lib.FileData"></a>

--------------------------------------------------------------
### FileData
--------------------------------------------------------------

```python
class FileData(Data)
```
``Data`` backend that reads from a local file via a buffer.

Opens the file in binary read mode and uses ``seek()`` + ``read()`` syscalls
for each access.  The file object is kept open for the lifetime of the
instance (shared with all associated ``Reader``s).

Args:
    path: Absolute or relative path to the file to read.

Raises:
    ValueError: If ``path`` is empty, ``None``, or does not exist.

#### Attributes

| Attribute | Default          |
| --------- | ---------------- |
| _path     | path             |
| length    | None             |
| _fobj     | open(path, 'rb') |

#### Functions

| Prototype                                                                                        |
| ------------------------------------------------------------------------------------------------ |
| def [`__init__`](#thirdparty.pparse.lib.FileData.__init__)``(path: Optional[str] = None) -> None |
| def [`peek`](#thirdparty.pparse.lib.FileData.peek)``(cursor: Cursor, length: int) -> bytes       |
| def [`seek`](#thirdparty.pparse.lib.FileData.seek)``(cursor: Cursor) -> int                      |
| def [`read`](#thirdparty.pparse.lib.FileData.read)``(cursor: Cursor, length: int) -> bytes       |
| def [`from_xml`](#thirdparty.pparse.lib.FileData.from_xml)``(xml_src: Any) -> FileData           |
| def [`to_xml`](#thirdparty.pparse.lib.FileData.to_xml)``() -> str                                |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileData.__init__"></a>


--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileData.peek"></a>


--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileData.seek"></a>


--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileData.read"></a>


--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileData.from_xml"></a>


--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileData.to_xml"></a>


<a id="thirdparty.pparse.lib.FileMmapData"></a>

--------------------------------------------------------------
### FileMmapData
--------------------------------------------------------------

```python
class FileMmapData(Data)
```
``Data`` backend that memory-maps a local file for zero-copy access.

Uses ``mmap`` and a ``memoryview`` overlay so that slice operations
return a ``memoryview`` without copying bytes.  This is the fastest
backend for local files when random access patterns are common.

Note: Untested in production use. (Unused/Legacy)

Args:
    path: Absolute or relative path to the file to map.

Raises:
    ValueError: If ``path`` is empty, ``None``, or does not exist.
    Exception: If ``mmap`` is not available on the platform.

#### Attributes

| Attribute | Default                                                      |
| --------- | ------------------------------------------------------------ |
| _path     | path                                                         |
| length    | None                                                         |
| _fobj     | open(path, 'rb')                                             |
| _mmap     | mmap.mmap(self._fobj.fileno(), 0, access=(mmap.ACCESS_READ)) |
| _mem      | memoryview(self._mmap)                                       |

#### Functions

| Prototype                                                                                                             |
| --------------------------------------------------------------------------------------------------------------------- |
| def [`__init__`](#thirdparty.pparse.lib.FileMmapData.__init__)``(path: Optional[str] = None) -> None                  |
| def [`_load_length`](#thirdparty.pparse.lib.FileMmapData._load_length)``() -> None                                    |
| def [`peek`](#thirdparty.pparse.lib.FileMmapData.peek)``(cursor: Cursor, length: int) -> memoryview                   |
| def [`seek`](#thirdparty.pparse.lib.FileMmapData.seek)``(cursor: Cursor) -> int                                       |
| def [`read`](#thirdparty.pparse.lib.FileMmapData.read)``(cursor: Cursor, length: int, mode: Any = None) -> memoryview |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileMmapData.__init__"></a>

#### def [`__init__`](#thirdparty.pparse.lib.FileMmapData.__init__)``(path: Optional[str] = None) -> None
Return a zero-copy ``memoryview`` slice at the cursor's position.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Number of bytes to expose.
  - Any - Unused; present for interface compatibility.
- **Returns:**
  - memoryview - A ``memoryview`` over the requested byte range.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileMmapData._load_length"></a>

#### def [`_load_length`](#thirdparty.pparse.lib.FileMmapData._load_length)``() -> None
Return a zero-copy ``memoryview`` slice at the cursor's position.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Number of bytes to expose.
  - Any - Unused; present for interface compatibility.
- **Returns:**
  - memoryview - A ``memoryview`` over the requested byte range.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileMmapData.peek"></a>

#### def [`peek`](#thirdparty.pparse.lib.FileMmapData.peek)``(cursor: Cursor, length: int) -> memoryview
Return a zero-copy ``memoryview`` slice at the cursor's position.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Number of bytes to expose.
  - Any - Unused; present for interface compatibility.
- **Returns:**
  - memoryview - A ``memoryview`` over the requested byte range.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileMmapData.seek"></a>

#### def [`seek`](#thirdparty.pparse.lib.FileMmapData.seek)``(cursor: Cursor) -> int
Return a zero-copy ``memoryview`` slice at the cursor's position.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Number of bytes to expose.
  - Any - Unused; present for interface compatibility.
- **Returns:**
  - memoryview - A ``memoryview`` over the requested byte range.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.FileMmapData.read"></a>

#### def [`read`](#thirdparty.pparse.lib.FileMmapData.read)``(cursor: Cursor, length: int, mode: Any = None) -> memoryview
Return a zero-copy ``memoryview`` slice at the cursor's position.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Number of bytes to expose.
  - Any - Unused; present for interface compatibility.
- **Returns:**
  - memoryview - A ``memoryview`` over the requested byte range.

<a id="thirdparty.pparse.lib.BytesIoData"></a>

--------------------------------------------------------------
### BytesIoData
--------------------------------------------------------------

```python
class BytesIoData(Data)
```
``Data`` backend backed by an in-memory ``io.BytesIO`` buffer.

Useful when the raw bytes are already in memory, e.g. when a file inside
a ZIP archive has been decompressed into a buffer and needs to be parsed
as its own extraction.

Args:
    bytes_io: The ``BytesIO`` buffer to read from.

Raises:
    ValueError: If ``bytes_io`` is ``None`` or is not a ``BytesIO`` instance.

#### Attributes

| Attribute | Default                         |
| --------- | ------------------------------- |
| _bytes_io | bytes_io                        |
| length    | len(self._bytes_io.getbuffer()) |

#### Functions

| Prototype                                                                                                      |
| -------------------------------------------------------------------------------------------------------------- |
| def [`__init__`](#thirdparty.pparse.lib.BytesIoData.__init__)``(bytes_io: Optional[io.BytesIO] = None) -> None |
| def [`_load_length`](#thirdparty.pparse.lib.BytesIoData._load_length)``() -> None                              |
| def [`open`](#thirdparty.pparse.lib.BytesIoData.open)``(offset: int = 0) -> Cursor                             |
| def [`peek`](#thirdparty.pparse.lib.BytesIoData.peek)``(cursor: Cursor, length: int) -> bytes                  |
| def [`seek`](#thirdparty.pparse.lib.BytesIoData.seek)``(cursor: Cursor) -> int                                 |
| def [`read`](#thirdparty.pparse.lib.BytesIoData.read)``(cursor: Cursor, length: int) -> bytes                  |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesIoData.__init__"></a>

#### def [`__init__`](#thirdparty.pparse.lib.BytesIoData.__init__)``(bytes_io: Optional[io.BytesIO] = None) -> None
Read ``length`` bytes.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesIoData._load_length"></a>

#### def [`_load_length`](#thirdparty.pparse.lib.BytesIoData._load_length)``() -> None
Read ``length`` bytes.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesIoData.open"></a>

#### def [`open`](#thirdparty.pparse.lib.BytesIoData.open)``(offset: int = 0) -> Cursor
Read ``length`` bytes.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesIoData.peek"></a>

#### def [`peek`](#thirdparty.pparse.lib.BytesIoData.peek)``(cursor: Cursor, length: int) -> bytes
Read ``length`` bytes.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesIoData.seek"></a>

#### def [`seek`](#thirdparty.pparse.lib.BytesIoData.seek)``(cursor: Cursor) -> int
Read ``length`` bytes.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesIoData.read"></a>

#### def [`read`](#thirdparty.pparse.lib.BytesIoData.read)``(cursor: Cursor, length: int) -> bytes
Read ``length`` bytes.
- **Parameters:**
  - Cursor - The ``Cursor`` indicating where to read from.
  - int - Max number of bytes to read.
- **Returns:**
  - bytes - Up to ``length`` bytes of data.

<a id="thirdparty.pparse.lib.Extraction"></a>

--------------------------------------------------------------
### Extraction
--------------------------------------------------------------

```python
class Extraction()
```
Abstract representation of a named data source with zero or more attached parsers.

An ``Extraction`` couples a raw data source (file, URL, in-memory buffer)
with the parsers that know how to interpret it.  Subclasses implement
``open()`` to return a ``Reader`` positioned at the start of the data.

Args:
    name: A human-readable name for this extraction (e.g. a filename).
    source: The parent this ``Extraction`` was derived from, if any.

#### Attributes

| Attribute    | Default |
| ------------ | ------- |
| _source      | source  |
| _name        | name    |
| _parser      | {}      |
| _result      | {}      |
| _extractions | []      |

#### Functions

| Prototype                                                                                                                               |
| --------------------------------------------------------------------------------------------------------------------------------------- |
| def [`__init__`](#thirdparty.pparse.lib.Extraction.__init__)``(name: Optional[str] = None, source: Optional[Extraction] = None) -> None |
| def [`name`](#thirdparty.pparse.lib.Extraction.name)``() -> Optional[str]                                                               |
| def [`set_name`](#thirdparty.pparse.lib.Extraction.set_name)``(name: str) -> Extraction                                                 |
| def [`add_result`](#thirdparty.pparse.lib.Extraction.add_result)``(id: Any, root_node: Optional[Node]) -> None                          |
| def [`add_parser`](#thirdparty.pparse.lib.Extraction.add_parser)``(id: str, parser: Optional[Parser]) -> None                           |
| def [`has_parser`](#thirdparty.pparse.lib.Extraction.has_parser)``(parser_id: str) -> bool                                              |
| def [`discover_parsers`](#thirdparty.pparse.lib.Extraction.discover_parsers)``(parser_registry: Dict[str, Any]) -> Extraction           |
| def [`open`](#thirdparty.pparse.lib.Extraction.open)``() -> Reader                                                                      |
| def [`scan_data`](#thirdparty.pparse.lib.Extraction.scan_data)``() -> Extraction                                                        |
| def [`from_xml`](#thirdparty.pparse.lib.Extraction.from_xml)``(xml_src: Any, xml_root: Any) -> Extraction                               |
| def [`to_xml`](#thirdparty.pparse.lib.Extraction.to_xml)``() -> str                                                                     |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.__init__"></a>

#### def [`__init__`](#thirdparty.pparse.lib.Extraction.__init__)``(name: Optional[str] = None, source: Optional[Extraction] = None) -> None
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.name"></a>

#### def [`name`](#thirdparty.pparse.lib.Extraction.name)``() -> Optional[str]
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.set_name"></a>

#### def [`set_name`](#thirdparty.pparse.lib.Extraction.set_name)``(name: str) -> Extraction
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.add_result"></a>

#### def [`add_result`](#thirdparty.pparse.lib.Extraction.add_result)``(id: Any, root_node: Optional[Node]) -> None
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.add_parser"></a>

#### def [`add_parser`](#thirdparty.pparse.lib.Extraction.add_parser)``(id: str, parser: Optional[Parser]) -> None
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.has_parser"></a>

#### def [`has_parser`](#thirdparty.pparse.lib.Extraction.has_parser)``(parser_id: str) -> bool
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.discover_parsers"></a>

#### def [`discover_parsers`](#thirdparty.pparse.lib.Extraction.discover_parsers)``(parser_registry: Dict[str, Any]) -> Extraction
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.open"></a>

#### def [`open`](#thirdparty.pparse.lib.Extraction.open)``() -> Reader
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.scan_data"></a>

#### def [`scan_data`](#thirdparty.pparse.lib.Extraction.scan_data)``() -> Extraction
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.from_xml"></a>

#### def [`from_xml`](#thirdparty.pparse.lib.Extraction.from_xml)``(xml_src: Any, xml_root: Any) -> Extraction
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Extraction.to_xml"></a>

#### def [`to_xml`](#thirdparty.pparse.lib.Extraction.to_xml)``() -> str
Stop and save the current state of ``Extraction`` to XML.
- **Returns:**
  - str - An XML string representation of this extraction.
- **Raises:**
  - NotImplementedError - Must be implemented by subclasses.

<a id="thirdparty.pparse.lib.BytesExtraction"></a>

--------------------------------------------------------------
### BytesExtraction
--------------------------------------------------------------

```python
class BytesExtraction(Extraction)
```
An ``Extraction`` backed by an existing ``Reader`` (bytes already in hand).

Used when the raw data is accessible via a ``Reader`` — for example, a
``Range`` wrapping a memory-mapped file or a ``BytesIoData`` cursor.
Exactly one of ``source`` or ``reader`` must be provided.

Args:
    name: A human-readable name for this extraction (e.g. relative filename).
    source: Parent ``Extraction`` to ``open`` a ``Reader``.
    reader: An existing ``Reader`` to use directly.

Note: Use only source xor reader, not both (i.e. one and only one must be set).

Raises:
    ValueError: If both or neither of ``source`` and ``reader`` are provided.

#### Attributes

| Attribute | Default |
| --------- | ------- |
| _reader   | reader  |

#### Functions

| Prototype                                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| def [`__init__`](#thirdparty.pparse.lib.BytesExtraction.__init__)``(name: Optional[str] = None, source: Optional[Extraction] = None, reader: Optional[Reader] = None) -> None |
| def [`open`](#thirdparty.pparse.lib.BytesExtraction.open)``() -> Reader                                                                                                       |
| def [`tell`](#thirdparty.pparse.lib.BytesExtraction.tell)``() -> int                                                                                                          |
| def [`from_xml`](#thirdparty.pparse.lib.BytesExtraction.from_xml)``(xml_src: Any, pparse_xml: Optional[Any] = None) -> BytesExtraction                                        |
| def [`to_xml`](#thirdparty.pparse.lib.BytesExtraction.to_xml)``() -> str                                                                                                      |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesExtraction.__init__"></a>


--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesExtraction.open"></a>


--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesExtraction.tell"></a>


--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesExtraction.from_xml"></a>


--------------------------------------------------------------


<a id="thirdparty.pparse.lib.BytesExtraction.to_xml"></a>


<a id="thirdparty.pparse.lib.Parser"></a>

--------------------------------------------------------------
### Parser
--------------------------------------------------------------

```python
class Parser()
```
Abstract base class for format-specific parsers attached to an ``Extraction``.

A ``Parser`` is responsible for lazily interpreting the bytes provided by
its ``Extraction`` and populating a tree of ``Node`` objects.  Concrete
subclasses override ``match_extension`` and ``match_magic`` so the framework
can auto-detect the right parser for a given data source.

If ``base_state_cls`` is provided the constructor automatically discovers
all transitive subclasses and registers them by name in ``_all_states``,
enabling state lookup by string name via ``_init_state_as_cls``. (Required for
XML load and resume.)

Args:
    source: The ``Extraction`` this parser will consume.
    id: A unique string identifier for this parser within the extraction.
    base_state_cls: Optional base class for the parser's state machine.
        All subclasses of this class are registered in ``_all_states``.

Raises:
    TypeError: If ``source`` is not an ``Extraction`` instance.

#### Attributes

| Attribute       | Default |
| --------------- | ------- |
| _id             | id      |
| _source         | source  |
| current         | None    |
| _all_states     | {}      |
| _base_state_cls | None    |

#### Functions

| Prototype                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------------- |
| def [`__init__`](#thirdparty.pparse.lib.Parser.__init__)``(source: Extraction, id: str, base_state_cls: Optional[Type[Any]] = None) -> None |
| def [`_init_state_as_cls`](#thirdparty.pparse.lib.Parser._init_state_as_cls)``(init_state: Union[str, Type[Any]]) -> Type[Any]              |
| def [`source`](#thirdparty.pparse.lib.Parser.source)``() -> Extraction                                                                      |
| def [`scan_data`](#thirdparty.pparse.lib.Parser.scan_data)``() -> None                                                                      |
| def [`match_extension`](#thirdparty.pparse.lib.Parser.match_extension)``(fname: str) -> bool                                                |
| def [`match_magic`](#thirdparty.pparse.lib.Parser.match_magic)``(cursor: Any) -> bool                                                       |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Parser.__init__"></a>

#### def [`__init__`](#thirdparty.pparse.lib.Parser.__init__)``(source: Extraction, id: str, base_state_cls: Optional[Type[Any]] = None) -> None
Return whether the magic bytes at the start of the data match this format.
- **Parameters:**
  - Any - A ``Reader`` positioned at the beginning of the data.
- **Returns:**
  - bool - ``True`` if the magic bytes match, ``False`` otherwise.
  - bool - The base implementation always returns ``False``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Parser._init_state_as_cls"></a>

#### def [`_init_state_as_cls`](#thirdparty.pparse.lib.Parser._init_state_as_cls)``(init_state: Union[str, Type[Any]]) -> Type[Any]
Return whether the magic bytes at the start of the data match this format.
- **Parameters:**
  - Any - A ``Reader`` positioned at the beginning of the data.
- **Returns:**
  - bool - ``True`` if the magic bytes match, ``False`` otherwise.
  - bool - The base implementation always returns ``False``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Parser.source"></a>

#### def [`source`](#thirdparty.pparse.lib.Parser.source)``() -> Extraction
Return whether the magic bytes at the start of the data match this format.
- **Parameters:**
  - Any - A ``Reader`` positioned at the beginning of the data.
- **Returns:**
  - bool - ``True`` if the magic bytes match, ``False`` otherwise.
  - bool - The base implementation always returns ``False``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Parser.scan_data"></a>

#### def [`scan_data`](#thirdparty.pparse.lib.Parser.scan_data)``() -> None
Return whether the magic bytes at the start of the data match this format.
- **Parameters:**
  - Any - A ``Reader`` positioned at the beginning of the data.
- **Returns:**
  - bool - ``True`` if the magic bytes match, ``False`` otherwise.
  - bool - The base implementation always returns ``False``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Parser.match_extension"></a>

#### def [`match_extension`](#thirdparty.pparse.lib.Parser.match_extension)``(fname: str) -> bool
Return whether the magic bytes at the start of the data match this format.
- **Parameters:**
  - Any - A ``Reader`` positioned at the beginning of the data.
- **Returns:**
  - bool - ``True`` if the magic bytes match, ``False`` otherwise.
  - bool - The base implementation always returns ``False``.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Parser.match_magic"></a>

#### def [`match_magic`](#thirdparty.pparse.lib.Parser.match_magic)``(cursor: Any) -> bool
Return whether the magic bytes at the start of the data match this format.
- **Parameters:**
  - Any - A ``Reader`` positioned at the beginning of the data.
- **Returns:**
  - bool - ``True`` if the magic bytes match, ``False`` otherwise.
  - bool - The base implementation always returns ``False``.

<a id="thirdparty.pparse.lib.Tensor"></a>

--------------------------------------------------------------
### Tensor
--------------------------------------------------------------

```python
class Tensor()
```
Abstract representation of a typed, shaped tensor stored in a binary format.

Subclasses are expected to implement all abstract methods to provide
access to the underlying data in a format-independent way.  The class
also provides lookup tables that map pparse dtype strings to struct
format characters, element sizes, and NumPy dtypes.

#### Attributes

| Attribute     | Default                                                                                                                                                                                  |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| STTYPE_STRUCT | {'I8': 'b', 'U8': 'B', 'I16': 'h', 'U16': 'H', 'I32': 'i', 'U32': 'I', 'I64': 'q', 'U64': 'Q', 'F32': 'f', 'F64': 'd'}                                                                   |
| STTYPE_SIZE   | {'I8': 1, 'U8': 1, 'I16': 2, 'U16': 2, 'I32': 4, 'U32': 4, 'I64': 8, 'U64': 8, 'F32': 4, 'F64': 8}                                                                                       |
| STTYPE_NP_MAP | {'F32': numpy.float32, 'F64': numpy.float64, 'F16': numpy.float16, 'I8': numpy.int8, 'I16': numpy.int16, 'I32': numpy.int32, 'I64': numpy.int64, 'U8': numpy.uint8, 'BOOL': numpy.bool_} |

#### Functions

| Prototype                                                                         |
| --------------------------------------------------------------------------------- |
| def [`get_type`](#thirdparty.pparse.lib.Tensor.get_type)``() -> str               |
| def [`get_shape`](#thirdparty.pparse.lib.Tensor.get_shape)``() -> List[int]       |
| def [`get_data_bytes`](#thirdparty.pparse.lib.Tensor.get_data_bytes)``() -> bytes |
| def [`as_array`](#thirdparty.pparse.lib.Tensor.as_array)``() -> Any               |
| def [`as_numpy`](#thirdparty.pparse.lib.Tensor.as_numpy)``() -> numpy.ndarray     |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Tensor.get_type"></a>

#### def [`get_type`](#thirdparty.pparse.lib.Tensor.get_type)``() -> str
Return the tensor data as a NumPy array typed to the tensor's dtype and shape.
- **Returns:**
  - numpy.ndarray - A ``numpy.ndarray`` with the appropriate dtype and shape.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Tensor.get_shape"></a>

#### def [`get_shape`](#thirdparty.pparse.lib.Tensor.get_shape)``() -> List[int]
Return the tensor data as a NumPy array typed to the tensor's dtype and shape.
- **Returns:**
  - numpy.ndarray - A ``numpy.ndarray`` with the appropriate dtype and shape.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Tensor.get_data_bytes"></a>

#### def [`get_data_bytes`](#thirdparty.pparse.lib.Tensor.get_data_bytes)``() -> bytes
Return the tensor data as a NumPy array typed to the tensor's dtype and shape.
- **Returns:**
  - numpy.ndarray - A ``numpy.ndarray`` with the appropriate dtype and shape.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Tensor.as_array"></a>

#### def [`as_array`](#thirdparty.pparse.lib.Tensor.as_array)``() -> Any
Return the tensor data as a NumPy array typed to the tensor's dtype and shape.
- **Returns:**
  - numpy.ndarray - A ``numpy.ndarray`` with the appropriate dtype and shape.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.Tensor.as_numpy"></a>

#### def [`as_numpy`](#thirdparty.pparse.lib.Tensor.as_numpy)``() -> numpy.ndarray
Return the tensor data as a NumPy array typed to the tensor's dtype and shape.
- **Returns:**
  - numpy.ndarray - A ``numpy.ndarray`` with the appropriate dtype and shape.

<a id="thirdparty.pparse.lib.PparseXml"></a>

--------------------------------------------------------------
### PparseXml
--------------------------------------------------------------

```python
class PparseXml()
```
Coordinator for XML-driven import of a pparse parse session.

``PparseXml`` is instantiated once per ``<pparse />`` XML document.  It
maintains a mapping from numeric result IDs to the ``BytesExtraction``
objects that own those results, acting as a cross-reference resolver
during the recursive import of ``<node />`` elements.

Args:
    xml: The root XML node (or string) representing the ``<pparse />``
        document being imported.

#### Attributes

| Attribute                 | Default |
| ------------------------- | ------- |
| xml                       | xml     |
| _result_ref_to_extraction | {}      |

#### Functions

| Prototype                                                                                                                          |
| ---------------------------------------------------------------------------------------------------------------------------------- |
| def [`__init__`](#thirdparty.pparse.lib.PparseXml.__init__)``(xml: Any) -> None                                                    |
| def [`add_result_ref`](#thirdparty.pparse.lib.PparseXml.add_result_ref)``(result_ref_id: int, extraction: BytesExtraction) -> None |
| def [`has_extraction`](#thirdparty.pparse.lib.PparseXml.has_extraction)``(result_ref_id: int) -> bool                              |
| def [`get_extraction`](#thirdparty.pparse.lib.PparseXml.get_extraction)``(result_ref_id: int) -> BytesExtraction                   |
| def [`from_xml`](#thirdparty.pparse.lib.PparseXml.from_xml)``(xml_src: Any) -> PparseXml                                           |

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.PparseXml.__init__"></a>

#### def [`__init__`](#thirdparty.pparse.lib.PparseXml.__init__)``(xml: Any) -> None
Load and resume from a ``<pparse />`` XML document into a live object graph.

Recursively imports the root extraction, all result references, and
all ``<node />`` elements, restoring the parser and context state for
each node.
- **Parameters:**
  - Any - A string, file path, or XmlNode representing the
``<pparse />`` document root.
- **Returns:**
  - PparseXml - A fully populated ``PparseXml`` instance with all extraction and
  - PparseXml - node references resolved.
- **Raises:**
  - ValueError - If the root element is not ``<pparse />``.
  - Exception - If required attributes or elements are missing.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.PparseXml.add_result_ref"></a>

#### def [`add_result_ref`](#thirdparty.pparse.lib.PparseXml.add_result_ref)``(result_ref_id: int, extraction: BytesExtraction) -> None
Load and resume from a ``<pparse />`` XML document into a live object graph.

Recursively imports the root extraction, all result references, and
all ``<node />`` elements, restoring the parser and context state for
each node.
- **Parameters:**
  - Any - A string, file path, or XmlNode representing the
``<pparse />`` document root.
- **Returns:**
  - PparseXml - A fully populated ``PparseXml`` instance with all extraction and
  - PparseXml - node references resolved.
- **Raises:**
  - ValueError - If the root element is not ``<pparse />``.
  - Exception - If required attributes or elements are missing.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.PparseXml.has_extraction"></a>

#### def [`has_extraction`](#thirdparty.pparse.lib.PparseXml.has_extraction)``(result_ref_id: int) -> bool
Load and resume from a ``<pparse />`` XML document into a live object graph.

Recursively imports the root extraction, all result references, and
all ``<node />`` elements, restoring the parser and context state for
each node.
- **Parameters:**
  - Any - A string, file path, or XmlNode representing the
``<pparse />`` document root.
- **Returns:**
  - PparseXml - A fully populated ``PparseXml`` instance with all extraction and
  - PparseXml - node references resolved.
- **Raises:**
  - ValueError - If the root element is not ``<pparse />``.
  - Exception - If required attributes or elements are missing.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.PparseXml.get_extraction"></a>

#### def [`get_extraction`](#thirdparty.pparse.lib.PparseXml.get_extraction)``(result_ref_id: int) -> BytesExtraction
Load and resume from a ``<pparse />`` XML document into a live object graph.

Recursively imports the root extraction, all result references, and
all ``<node />`` elements, restoring the parser and context state for
each node.
- **Parameters:**
  - Any - A string, file path, or XmlNode representing the
``<pparse />`` document root.
- **Returns:**
  - PparseXml - A fully populated ``PparseXml`` instance with all extraction and
  - PparseXml - node references resolved.
- **Raises:**
  - ValueError - If the root element is not ``<pparse />``.
  - Exception - If required attributes or elements are missing.

--------------------------------------------------------------


<a id="thirdparty.pparse.lib.PparseXml.from_xml"></a>

#### def [`from_xml`](#thirdparty.pparse.lib.PparseXml.from_xml)``(xml_src: Any) -> PparseXml
Load and resume from a ``<pparse />`` XML document into a live object graph.

Recursively imports the root extraction, all result references, and
all ``<node />`` elements, restoring the parser and context state for
each node.
- **Parameters:**
  - Any - A string, file path, or XmlNode representing the
``<pparse />`` document root.
- **Returns:**
  - PparseXml - A fully populated ``PparseXml`` instance with all extraction and
  - PparseXml - node references resolved.
- **Raises:**
  - ValueError - If the root element is not ``<pparse />``.
  - Exception - If required attributes or elements are missing.
