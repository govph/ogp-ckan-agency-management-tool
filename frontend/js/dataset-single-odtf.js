function deleteDataset(obj){
    $("body").append($("<div>", { class: "modal fade", id: "deleteDatasetModal", "tabindex": "-1", "role": "dialog", "aria-labelledby": "deleteDatasetModalLabel", "aria-hidden": "true" }).html(
                $("<div>", { class: "modal-dialog" }).html(
                    $("<form>", { action: "/dataset/" + datasetID + "/edit", method: "POST", id: "deleteDatasetForm" }).html(
                    $("<div>", { class: "modal-content" }).html(
                        $("<div>", { class: "modal-header" }).html(
                            $("<button>", { class: "close", "data-dismiss": "modal", type: "button", "aria-hidden": "true", text: "×" }).add(
                            $("<h3>", { class: "modal-title", id: "deleteDatasetModalLabel", text: "Delete Dataset" }))
                        ).add(
                            $("<div>", { class: "modal-body" }).html(
                                $("<h4>", { class: "", text: "Are you sure you want to delete this dataset?" }).add(
                                $("<input>", { type: "hidden", name: "delete_dataset", value: "1" }))
                            )
                        ).add(
                            $("<div>", { class: "modal-footer" }).html(
                                $("<div>", { class: "row" }).html(
                                $("<div>", { class: "col-lg-6" }).html(
                                    $("<button>", { type: "button", "data-dismiss": "modal", class: "btn btn-block btn-danger", text: "Cancel" })).add(
                                $("<div>", { class: "col-lg-6" }).html(
                                    $("<button>", { type: "submit", class: "btn btn-block btn-success", text: " Continue" }))))))
                        )
                    ))
                )
            );
    $("#deleteDatasetModal").modal({ show: true, backdrop: "static", keyboard: false }).on("shown.bs.modal", function (){
        $("#deleteDatasetForm").submit(function (e) {
            $(this).find("button").prop("disabled", true);
            $(this).find("button:submit").prepend($("<i>", { class: "fa fa-fw fa-spin fa-circle-o-notch" }));
        });
    }).on("hidden.bs.modal", function (){
        $(this).remove();
    });
}

function cancelDeleteDataset(obj){
    $("body").append(
        $("<div>", { class: "modal fade", id: "cancelDeleteDatasetModal", "tabindex": "-1", "role": "dialog", "aria-labelledby": "cancelDeleteDatasetModalLabel", "aria-hidden": "true" }).html(
                $("<div>", { class: "modal-dialog" }).html(
                    $("<form>", { action: "/dataset/" + datasetID + "/edit", method: "POST", id: "cancelDeleteDatasetForm" }).html(
                    $("<div>", { class: "modal-content" }).html(
                        $("<div>", { class: "modal-header" }).html(
                            $("<button>", { class: "close", "data-dismiss": "modal", type: "button", "aria-hidden": "true", text: "×" }).add(
                            $("<h3>", { class: "modal-title", id: "cancelDeleteDatasetModalLabel", text: "Cancel for Deletion Request" }))
                        ).add(
                            $("<div>", { class: "modal-body" }).html(
                                $("<h4>", { class: "", text: "Are you sure you want to cancel this request?" }).add(
                                $("<input>", { type: "hidden", name: "cancel_delete_dataset", value: "1" }))
                            )
                        ).add(
                            $("<div>", { class: "modal-footer" }).html(
                                $("<div>", { class: "row" }).html(
                                $("<div>", { class: "col-lg-6" }).html(
                                    $("<button>", { type: "button", "data-dismiss": "modal", class: "btn btn-block btn-danger", text: "Cancel" })).add(
                                $("<div>", { class: "col-lg-6" }).html(
                                    $("<button>", { type: "submit", class: "btn btn-block btn-success", text: " Continue" }))))))
                        )
                    ))
                )
            );
    $("#cancelDeleteDatasetModal").modal({ show: true, backdrop: "static", keyboard: false }).on("shown.bs.modal", function (){
        $("#cancelDeleteDatasetForm").submit(function (e) {
            $(this).find("button").prop("disabled", true);
            $(this).find("button:submit").prepend($("<i>", { class: "fa fa-fw fa-spin fa-circle-o-notch" }));
        });
    }).on("hidden.bs.modal", function (){
        $(this).remove();
    });
}

function publishedDataset(obj){
    $("body").append(
        $("<div>", { class: "modal fade", id: "publishedDatasetModal", "tabindex": "-1", "role": "dialog", "aria-labelledby": "publishedDatasetModalLabel", "aria-hidden": "true" }).html(
            $("<div>", { class: "modal-dialog" }).html(
                $("<form>", { action: "/dataset/" + datasetID + "/status", method: "POST", id: "publishedDatasetForm" }).html(
                    $("<div>", { class: "modal-content" }).html(
                        $("<div>", { class: "modal-header" }).html(
                            $("<button>", { class: "close", "data-dismiss": "modal", type: "button", "aria-hidden": "true", text: "×" }).add(
                            $("<h3>", { class: "modal-title", id: "publishedDatasetModalLabel", text: "Select a Department" }))
                        ).add(
                            $("<div>", { class: "modal-body" }).html(
                                $("<h3>", { class: "text-center" }).html(
                                    $("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
                                $("<h4>", { class: "text-center", text: "Loading Departments" }))
                            )
                        ).add(
                            $("<div>", { class: "modal-footer" }).html(
                                $("<div>", { class: "col-lg-6" }).html(
                                    $("<button>", { type: "button", "data-dismiss": "modal", class: "btn btn-block btn-danger", text: "Cancel", disabled: "" })).add(
                                $("<div>", { class: "col-lg-6" }).html(
                                    $("<button>", { type: "submit", class: "btn btn-block btn-success", text: " Continue", disabled: "" })))))
                        )
                    ))
                )
    );
    $("#publishedDatasetModal").modal({ show: true, backdrop: "static", keyboard: false }).on("shown.bs.modal", function (){
        xhr_request = $.getJSON("http://api.data.gov.ph/catalogue/api/action/organization_list?callback=?")
        .done(function(d) {
            $("#publishedDatasetModal").find(".modal-footer").find("button").prop("disabled", false);
            $("#publishedDatasetModal").find(".modal-body").html(
                $("<select>", { class: "form-control", name: "owner_org", id: "publishedDatasetDepartment" }).add(
                $("<input>", { type: "hidden", name: "status", value: "PUBLISHED" })));
            for(i=0;i<d.result.length;i++){
                $("#publishedDatasetDepartment").append($("<option>", { value: d.result[i], text: d.result[i].toUpperCase().split("-").join(" ") }));
            }
        })
        .fail(function( jqxhr, textStatus, error ) {
            $("#publishedDatasetModal").find(".modal-body").html($("<h3>", { class: "text-center" }).html(
                $("<i>", { class: "fa fa-2x fa-warning" })).add(
                $("<h4>", { class: "text-center", text: "Could not load the departments." })));
            $("#publishedDatasetModal").find(".modal-footer").find("button.btn-danger").prop("disabled", false);
        });
        $("#publishedDatasetForm").submit(function (e) {
            $.this = $(this);
            $.this.find("button").prop("disabled", true);
            $.this.find("button:submit").prepend($("<i>", { class: "fa fa-fw fa-spin fa-circle-o-notch" }));
        });
    }).on("hidden.bs.modal", function (){
        $(this).remove();
        xhr_request.abort();
    });
}

function forCleanUpDataset(obj){
    $(".dataset-action").find("button").prop("disabled", true).prepend($("<i>", { class: "fa fa-fw fa-spin fa-circle-o-notch" }));
    $.ajax({
        url: $(obj).data("url"),
        type: "POST",
        data: {status: "FOR CLEAN UP"},
        success: function (data){
            location.reload();
        },
        error: function (){
            $(".dataset-action").find("button").prop("disabled", false).children("i").remove();
        }
    });
}

function sendBackDataset(){
    $("body").append(
        $("<div>", { class: "modal fade", id: "sendBackDatasetModal", "tabindex": "-1", "role": "dialog", "aria-labelledby": "sendBackDatasetModalLabel", "aria-hidden": "true" }).html(
            $("<div>", { class: "modal-dialog" }).html(
                $("<form>", { action: "/dataset/" + datasetID + "/status", method: "POST", id: "sendBackDatasetForm" }).html(
                    $("<div>", { class: "modal-content" }).html(
                        $("<div>", { class: "modal-header" }).html(
                            $("<button>", { class: "close", "data-dismiss": "modal", type: "button", "aria-hidden": "true", text: "×" }).add(
                            $("<h3>", { class: "text-center modal-title", id: "sendBackDatasetModalLabel" }).html(
                                $("<i>", { class: "fa fa-fw fa-3x fa-reply" }).add(
                                $("<p>", { text: "Sent Back Comment" }))).add(
                            $("<p>", { class: "text-center no-margin", text: "Please provide comments on why this dataset was sent back." })))
                        ).add(
                            $("<div>", { class: "modal-body" }).html(
                                $("<p>", { text: " Message"}).prepend(
                                    $("<i>", { class: "fa fa-fw fa-comment" })).add(
                                $("<textarea>", { class: "form-control", rows: "7", id: "dataset-comment", required: ""}))
                            )
                        ).add(
                            $("<div>", { class: "modal-footer" }).html(
                                $("<div>", { class: "col-lg-6" }).html(
                                    $("<button>", { type: "button", "data-dismiss": "modal", class: "btn btn-block btn-danger", text: "Cancel" })).add(
                                $("<div>", { class: "col-lg-6" }).html(
                                    $("<button>", { type: "submit", class: "btn btn-block btn-success", text: " Continue" })))))
                        )
                    )
            )
        )
    );
    $("#sendBackDatasetModal").modal({ show: true, backdrop: "static", keyboard: false }).on("shown.bs.modal", function (){
        $("#sendBackDatasetForm").submit(function (e) {
            $.this = $(this);
            $.this.find("textarea").prop("disabled", true);
            $.this.find("button").prop("disabled", true);
            $.this.find("button:submit").prepend($("<i>", { class: "fa fa-fw fa-spin fa-circle-o-notch" }));
            $.ajax({
                url: $(this).attr("action"),
                type: "POST",
                data: {status: "SENT BACK", comment: $("#dataset-comment").val()},
                success: function (data){
                    location.reload();
                },
                error: function (){
                    $.this.find("textarea").prop("disabled", false);
                    $.this.find("button").prop("disabled", false);
                    $.this.find("button:submit").children("i").remove();
                }
            });
            e.preventDefault();
        });
    }).on("hidden.bs.modal", function (){
        $(this).remove();
    });
}