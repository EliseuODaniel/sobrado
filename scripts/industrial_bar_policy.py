"""Decisão do proprietário: versões industriais não possuem geladeira no bar."""
import bpy


def bar_fridges():
    return [obj for obj in bpy.data.objects if obj.type == 'EMPTY' and 'geladeira' in obj.name.casefold() and 'bar' in obj.name.casefold()]


def remove_bar_fridges():
    removed = []
    for root in bar_fridges():
        family = [root, *root.children_recursive]
        removed.extend(obj.name for obj in family)
        for obj in reversed(family):
            if bpy.data.objects.get(obj.name): bpy.data.objects.remove(obj, do_unlink=True)
    assert not bar_fridges()
    return sorted(removed)
