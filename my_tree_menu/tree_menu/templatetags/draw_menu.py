from django import template
from django.urls import NoReverseMatch, resolve

from ..models import Menu

# Регистрируем библиотеку тегов
register = template.Library()


# Создаем inclusion тег, который будет рендерить шаблон 'tree_menu/menu.html'
@register.inclusion_tag('tree_menu/menu.html', takes_context=True)
def draw_menu(context, menu_name):
    """
    Кастомный тег для отрисовки древовидного меню.
    :param context: контекст шаблона (автоматически передается Django)
    :param menu_name: название меню, которое нужно отрисовать
    """
    # Получаем объект запроса из контекста
    request = context['request']
    # Получаем текущий URL пути
    current_url = request.path_info

    try:
        # Пытаемся получить меню по имени с предварительной загрузкой
        # связанных пунктов prefetch_related('items') обеспечивает
        # загрузку всех пунктов меню одним запросом
        menu = Menu.objects.prefetch_related('items').get(name=menu_name)
    except Menu.DoesNotExist:
        # Если меню не найдено, возвращаем пустой контекст
        return {'menu': None}

    # Получаем все пункты меню
    menu_items = menu.items.all()

    # Определяем активный пункт меню
    active_item = None
    for item in menu_items:
        try:
            item_url = item.get_url()
            # Проверяем точное совпадение URL
            if item_url == current_url:
                active_item = item
                break
            # Проверяем named URL (если он указан в пункте меню)
            if item.named_url:
                try:
                    resolved = resolve(current_url)
                    if resolved.url_name == item.named_url:
                        active_item = item
                        break
                except Exception:
                    continue
        except NoReverseMatch:
            continue

    # Рекурсивная функция для построения дерева меню
    def build_menu_tree(items, parent=None):
        tree = []
        for item in items:
            if item.parent == parent:
                children = build_menu_tree(items, item)

                # Проверка активного состояния
                is_active = (active_item and active_item.pk == item.pk)
                is_parent_active = False

                if active_item:
                    # Проверяем всех родителей активного элемента
                    parent_ptr = active_item.parent
                    while parent_ptr:
                        if parent_ptr.pk == item.pk:
                            is_parent_active = True
                            break
                        parent_ptr = parent_ptr.parent

                    if active_item.pk == item.pk:
                        is_parent_active = True

                tree.append({
                    'item': item,
                    'children': children,
                    'is_active': is_active,
                    'is_parent_active': is_parent_active,
                })
        return tree

    # Строим полное дерево меню (начиная с корневых элементов)
    menu_tree = build_menu_tree(menu_items)

    # Возвращаем контекст для шаблона menu.html
    return {
        'menu': menu,
        'menu_tree': menu_tree,
        'current_url': current_url,
    }
