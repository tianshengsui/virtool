from typing import Callable

from aiohttp import web

import virtool.templates
import virtool.utils
from virtool.api.response import not_found


@web.middleware
async def middleware(req: web.Request, handler: Callable):
    is_api_call = req.path.startswith("/api")

    try:
        response = await handler(req)

        if not is_api_call and response.status == 404:
            return handle_404(req)

        return response

    except web.HTTPException as ex:
        if is_api_call:
            return not_found()

        if ex.status == 404:
            return handle_404(req)

        raise


def handle_404(req: web.Request):
    template = virtool.templates.setup_template_env.get_template("error_404.html")

    static_hash = virtool.utils.get_static_hash(req)

    html = template.render(hash=static_hash)

    return web.Response(body=html, content_type="text/html", status=404)
