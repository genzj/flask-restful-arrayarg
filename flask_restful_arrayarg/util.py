# -*- encoding: utf-8 -*-
def cut_key(key):
    if not key:
        return []

    assert key[0] == '['
    key = key.strip()
    cuts = []
    l = 0
    r = 0
    while True:
        r = key[l:].find(']') + l
        cuts.append(key[l + 1:r])
        if '[' in key[r:]:
            l = key[r:].find('[') + r
        else:
            break
    if r != len(key) - 1:
        raise ValueError('invalid key %r' % (key,))
    return cuts
