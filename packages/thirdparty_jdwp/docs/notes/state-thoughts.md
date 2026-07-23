




JDWP usage begs to store state. When doing JDWP queries, what should we cache and what isn't worth caching?

My hunch is that we want to cache everything, but different types of data have different life expectancy. In the life of a single stack frame, we may find ourselves able to cache EVERYTHING. But stack frames only live while the VM is suspended. Once the VM is resumed, the stack frames go away and the ids could be reused the next time the VM is suspended.

If we cache a stackframe between suspensions, its more of an archived state.

FrameIDs (and by extension their values) are the most unstable ID type.

The next most unstable ID are objectIDs and stringIDs. This is because these are objects that are stored on the JVM heap and can be reclaimed by the garbage collector.

Next in line are ThreadIDs or ThreadGroupIDs. They are alive for the life of a individual thread. Its not uncommon for a thread to be started and killed with a similar life span of an object.

More stable IDs include ClassObjectID, ReferenceTypeID, MethodID, FieldID, and ClassLoaderID. These IDs are loaded classes in the JVM that the JVM needs to always have available, espcially if there is a reference to any one of them in any of the objectIDs. 

Tightly coupled cache:
- ClassObjectID
- ReferenceTypeID
- MethodID
- FieldID
- ClassLoaderID

Loosely coupled cache:
- ThreadID
- ThreadGroupID

Local-only cache:
- FrameID


When we find an object of interest and its on the heap. We can watch that object and request its values when ever we want (e.g. break, step, on-event). 

When we request the values of an object, we want to allow the user to request the object by objectID or by a local python reference (with the objectID under the hood). When we have the reference to an object, we want to be able to see metadata about a reference.


class ObjectRef():
