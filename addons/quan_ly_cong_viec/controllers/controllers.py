# -*- coding: utf-8 -*-
# from odoo import http


# class NhanSu(http.Controller):
#     @http.route('/nhan_su/nhan_su', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nhan_su/nhan_su/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('nhan_su.listing', {
#             'root': '/nhan_su/nhan_su',
#             'objects': http.request.env['nhan_su.nhan_su'].search([]),
#         })

#     @http.route('/nhan_su/nhan_su/objects/<model("nhan_su.nhan_su"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nhan_su.object', {
#             'object': obj
#         })
