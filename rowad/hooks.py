# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "rowad"
app_title = "Rowad"
app_publisher = "GreyCube Technologies"
app_description = "customization for Rowad"
app_icon = "octicon octicon-home-fill"
app_color = "green"
app_email = "admin@greycube.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/rowad/css/rowad.css"
# app_include_js = "/assets/rowad/js/rowad.js"

# include js, css files in header of web template
# web_include_css = "/assets/rowad/css/rowad.css"
# web_include_js = "/assets/rowad/js/rowad.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Sales Order" : "public/js/sales_order.js",
    "Delivery Note" : "public/js/delivery_note.js",
    "Item" : "public/js/item.js",
	"Task" : "public/js/task.js",
	"Maintenance Schedule" : "public/js/maintenance_schedule.js",
	"Maintenance Visit" : "public/js/maintenance_visit.js"
    }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "rowad.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "rowad.install.before_install"
# after_install = "rowad.install.after_install"
after_migrate = "rowad.hook_methods.after_migrate"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "rowad.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Order": {
		"before_submit": "rowad.api.validate_sales_order_item_user_allocation",
	},
	"Task": {
		"validate": "rowad.api.validate_task_and_create_delivery_note_maintenance_schedule",
	}    
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"rowad.tasks.all"
# 	],
# 	"daily": [
# 		"rowad.tasks.daily"
# 	],
# 	"hourly": [
# 		"rowad.tasks.hourly"
# 	],
# 	"weekly": [
# 		"rowad.tasks.weekly"
# 	]
# 	"monthly": [
# 		"rowad.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "rowad.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "rowad.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "rowad.task.get_dashboard_data"
# }

