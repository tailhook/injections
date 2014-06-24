from collections import defaultdict, deque


class CyclicDependencies(RuntimeError):

    def __init__(self, objects):
        self.objects_in_cycle = objects
        super(CyclicDependencies, self).__init__("The objects {!r} "
                    "are in cyclic dependency. You must resolve them in "
                    "proper order manually.".format(objects))


def topologically_sorted(objects):

    refs = {}
    backrefs = defaultdict(set)
    queue = deque()

    for name, obj in objects.items():
        deps = getattr(obj, '__injections__', None)
        if not deps or getattr(obj, '__injections_source__', None):
            # Already injected objects are like those not having dependencies
            queue.append(name)
            continue
        cur_refs = set(d.name for d in deps.values())
        refs[name] = cur_refs
        for ref in cur_refs:
            backrefs[ref].add(name)
            if name in refs.get(ref, ()):
                raise CyclicDependencies({
                    name: objects[name],
                    ref: objects[ref],
                    })

    while queue:
        obj = queue.popleft()
        yield objects[obj]

        for dep in backrefs.pop(obj, ()):
            cur_refs = refs[dep]
            cur_refs.remove(obj)
            if not cur_refs:
                queue.append(dep)

    if backrefs:
        # There is aready an error, but we should o our best to discover
        # which objects are in cycle, so it's easier to fix by user

        # Basically we reverse dependencies and do same topology sort
        # in the reversed graph we will have same nodes in cycle but we
        # remove nodes that depend on it

        queue = deque(set(refs) - set(backrefs))
        while queue:
            obj = queue.popleft()

            for dep in refs[obj]:
                cur_refs = backrefs[dep]
                cur_refs.remove(obj)
                if not cur_refs:
                    del backrefs[dep]
                    queue.append(dep)

        raise CyclicDependencies({k: objects[k] for k in backrefs})
