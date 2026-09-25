// Copyright (c) 2026, Guruprasad and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Delivery Order", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Delivery Order", {

    setup(frm) {
        frm.set_query("assigned_rider", function () {
            return {
                filters: {
                    status: "Active",
                    assigned_zone: frm.doc.delivery_zone
                }
            };
        });
    },

    refresh(frm) {
        if (frm.doc.status === "In Transit") {
            frm.dashboard.add_indicator("In Transit", "orange");
        }
        else if (frm.doc.status === "Delivered") {
            frm.dashboard.add_indicator("Delivered", "green");
        }
        else if (frm.doc.status === "Delivery Failed") {
            frm.dashboard.add_indicator("Delivery Failed", "red");
        } 
        else if (frm.doc.status === "Re-attempt Scheduled") {
            frm.dashboard.add_indicator("Re-attempt Scheduled", "orange");
        }

        if (frm.doc.status === "In Transit" || frm.doc.status === "Re-attempt Scheduled") {
            frm.add_custom_button("Log Delivery Attempt", function () {

                let dialog = new frappe.ui.Dialog({
                    title: "Log Delivery Attempt",

                    fields: [
                        {
                            label: "Outcome",
                            fieldname: "outcome",
                            fieldtype: "Select",
                            options: "Delivered\nFailed",
                            reqd: 1
                        },
                        {
                            label: "Failure Reason",
                            fieldname: "failure_reason",
                            fieldtype: "Small Text"
                        }
                    ],

                    primary_action_label: "Submit",

                    primary_action(values) {

                        if (values.outcome === "Failed" && !values.failure_reason) {
                            frappe.msgprint("Failure Reason is mandatory when Outcome is Failed.");
                            return;
                        }

                        frappe.call({
                            method: "dashpoint.api.record_delivery_attempt",
                            args: {
                                delivery_order_name: frm.doc.name,
                                outcome: values.outcome,
                                failure_reason: values.failure_reason
                            },
                            callback: function () {
                                dialog.hide();
                                frm.reload_doc();
                            }
                        });
                    }
                });

                dialog.show();
            });
        }

       
        frm.add_custom_button("Reassign Rider", function () {

            frappe.prompt(
                [
                    {
                        label: "New Rider",
                        fieldname: "new_rider",
                        fieldtype: "Link",
                        options: "Rider",
                        reqd: 1
                    }
                ],

                function (values) {

                    frappe.confirm("Are you sure you want to reassign the rider?",

                        function () {

                            frappe.call({
                                method: "frappe.client.set_value",
                                args: {
                                    doctype: "Delivery Order",
                                    name: frm.doc.name,
                                    fieldname: "assigned_rider",
                                    value: values.new_rider
                                },

                                callback: function () {
                                    frm.trigger("assigned_rider");
                                }
                            });

                        }
                    );

                },

                "Reassign Rider",
                "Reassign"
            );
        });
    },

    assigned_rider(frm) {
        if (!frm.doc.assigned_rider) {
            return;
        }

        frappe.db.get_value("Rider", frm.doc.assigned_rider, "assigned_zone").then(r => {

            if (r.message && r.message.assigned_zone !== frm.doc.delivery_zone) {
                frappe.msgprint("Warning: Rider's assigned zone does not match the Delivery Zone.");
            }

        });
    }

});

frappe.ui.form.on("Packaging Usage Entry", {

    quantity(frm, cdt, cdn) { 

        let row = locals[cdt][cdn];

        frappe.model.set_value(cdt, cdn, "total_price", (row.quantity || 0) * (row.unit_price || 0));
 
    }
});

