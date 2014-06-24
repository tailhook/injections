from collections import defaultdict, deque


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
                raise RuntimeError("The objects {!r}:{!r} and {!r}:{!r} "
                    "have cyclic dependency. You must resolve them in "
                    "proper order manually.")

    while queue:
        obj = queue.popleft()
        yield objects[obj]

        for dep in backrefs[obj]:
            cur_refs = refs[dep]
            cur_refs.remove(obj)
            if not cur_refs:
                queue.append(dep)
