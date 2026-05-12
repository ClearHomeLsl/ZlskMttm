def get_page_size(page, page_size, model_obj):
    try:
        page = int(page)
        page_size = int(page_size)
        # 限制最大每页数量，防止恶意请求
        page_size = min(page_size, 100)
    except ValueError:
        page = 1
        page_size = 20

    # 计算起始和结束位置
    start = (page - 1) * page_size
    end = start + page_size
    # 获取总记录数
    total_count = model_obj.count()
    data = model_obj.order_by("-create_at")[start:end]

    # 计算总页数
    total_pages = (total_count + page_size - 1) // page_size
    return page, page_size, data, total_pages