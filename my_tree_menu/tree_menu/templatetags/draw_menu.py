from django import template
from django.urls import resolve

from ..models import Menu


# Регистрируем библиотеку тегов
register = template.Library()


def get_current_menu(menu_name):
    """Получает меню из БД с предзагрузкой элементов"""
    try:
        return Menu.objects.prefetch_related("items").get(name=menu_name)
    except Menu.DoesNotExist:
        return None


def find_active_item(menu_items, current_url):
    """Определяет активный пункт меню с кэшированием resolved URL"""
    resolved_url_name = None

    for item in menu_items:
        # Проверка прямого совпадения URL
        if item.get_url() == current_url:
            return item

        # Проверка named URL (ленивое разрешение)
        if item.named_url:
            if resolved_url_name is None:
                try:
                    resolved_url_name = resolve(current_url).url_name
                except Exception:
                    continue

            if item.named_url == resolved_url_name:
                return item

    return None


def is_item_active(item, active_item):
    """Проверяет, является ли пункт активным"""
    return active_item and active_item.pk == item.pk


def is_parent_active(item, active_item):
    """Проверяет, является ли пункт родителем активного"""
    if not active_item:
        return False

    parent_ptr = active_item.parent
    while parent_ptr:
        if parent_ptr.pk == item.pk:
            return True
        parent_ptr = parent_ptr.parent

    return active_item.pk == item.pk


def build_menu_tree(items, active_item, parent=None):
    """Рекурсивно строит дерево меню с флагами активности"""
    tree = []
    for item in items:
        if item.parent == parent:
            children = build_menu_tree(items, active_item, item)
            tree.append(
                {
                    "item": item,
                    "children": children,
                    "is_active": is_item_active(item, active_item),
                    "is_parent_active": is_parent_active(item, active_item),
                }
            )
    return tree


@register.inclusion_tag("tree_menu/menu.html", takes_context=True)
def draw_menu(context, menu_name):
    """Основной тег для отрисовки меню"""
    request = context.get("request")
    if not request:
        return {"menu": None}

    menu = get_current_menu(menu_name)
    if not menu:
        return {"menu": None}

    menu_items = menu.items.all()
    active_item = find_active_item(menu_items, request.path_info)
    menu_tree = build_menu_tree(menu_items, active_item)

    return {
        "menu": menu,
        "menu_tree": menu_tree,
        "current_url": request.path_info,
    }
