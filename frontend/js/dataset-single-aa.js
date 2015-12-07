function flagDataset(obj){
    $("body").append(
        $("<div>", { class: "modal fade", id: "flagDatasetModal", "tabindex": "-1", "role": "dialog", "aria-labelledby": "flagDatasetModalLabel", "aria-hidden": "true" }).html(
            $("<div>", { class: "modal-dialog" }).html(
                $("<form>", { action: "/dataset/" + datasetID + "/edit", method: "POST", id: "flagDatasetForm" }).html(
                    $("<div>", { class: "modal-content" }).html(
                        $("<div>", { class: "modal-header" }).html(
                            $("<button>", { class: "close", "data-dismiss": "modal", type: "button", "aria-hidden": "true", text: "×" }).add(
                            $("<h3>", { class: "text-center modal-title", id: "flagDatasetModalLabel" }).html(
                                $("<i>", { class: "fa fa-fw fa-3x fa-trash" }).add(
                                $("<p>", { text: "Flag for Deletion Comment" }))).add(
                            $("<p>", { class: "text-center no-margin", text: "Please provide comments on why this dataset was flagged for deletion." })))
                        ).add(
                            $("<div>", { class: "modal-body" }).html(
                                $("<p>", { text: " Message"}).prepend(
                                    $("<i>", { class: "fa fa-fw fa-comment" })).add(
                                $("<textarea>", { class: "form-control", rows: "7", id: "dataset-comment", name: "dataset_comment", required: ""}).add(
                                $("<input>", { type: "hidden", name: "flag_dataset", value: "1"})))
                            )
                        ).add(
                            $("<div>", { class: "modal-footer" }).html(
                                $("<div>", { class: "row" }).html(
                                $("<div>", { class: "col-lg-6" }).html(
                                    $("<button>", { type: "button", "data-dismiss": "modal", class: "btn btn-block btn-danger", text: "Cancel" })).add(
                                $("<div>", { class: "col-lg-6" }).html(
                                    $("<button>", { type: "submit", class: "btn btn-block btn-success", text: " Continue" })))))
                            )
                        )
                    ))
                )
            );
    $("#flagDatasetModal").modal({ show: true, backdrop: "static", keyboard: false }).on("shown.bs.modal", function (){
        $("#flagDatasetForm").submit(function (e) {
            $(this).find("button").prop("disabled", true);
            $(this).find("button:submit").prepend($("<i>", { class: "fa fa-fw fa-spin fa-circle-o-notch" }));
        });
        $(this).find("textarea.form-control").focus();
    }).on("hidden.bs.modal", function (){
        $(this).remove();
    });
}
