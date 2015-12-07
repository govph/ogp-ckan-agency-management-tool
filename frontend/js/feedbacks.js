var currentRequest = undefined;

$(document).ready(function (){
	loadForReviewFeedbacks();
});

$(function(){
	$("#for-review-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadForReviewFeedbacks();
	});
	$("#approved-feedback-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadApprovedFeedbacks();
	});
	$("#disapproved-feedback-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadDisapprovedFeedbacks();
	});
});

function loadForReviewFeedbacks(){
	$("#for-review").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Submissions" })));
	currentRequest = $.ajax({
		url: "/feedback?ajax=1&status=PENDING",
		success: function (data){
			if(data){
				try{
					if(data.feedbacks.length == 0){
						$("#for-review").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No pending user submissions." })));
					}
					else{
						$("#for-review").html($("<div>", { class: "feedbacks-list col-lg-12", id: "for-review-feedbacks-list" }))
						var counter = 0;
						for(i=0;i<data.feedbacks.length;i++){
							counter += 1;
							$("#for-review-feedbacks-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "feedbacks-item feedbacks-item"+counter+" col-lg-12" }).html(
										$("<div>", { class: "feedbacks-item-keys feedbacks-item-keys"+counter+" col-lg-9" }).add(
										$("<div>", { class: "feedbacks-item-content feedbacks-item-content"+counter+" col-lg-3 text-right" })))).add(
								$("<hr>")));

							for (var key in data.feedbacks[i].additional_data) {
								if(key == "id" || key == "type"){
									continue
								}
								var value = data.feedbacks[i].additional_data[key];
								if(key == "file"){
									key = "file";
									value = $("<a>", { href: value.file_url, target: "_blank", text: data.feedbacks[i].additional_data["file"]["file_name"] })
								}
								$(".feedbacks-item-keys" + counter).append(
									$("<div>", { class: "row" }).html(
									$("<div>", { class: "col-lg-5 text-right" }).html(
										$("<p>", { text: key.split('_').join(' ').toUpperCase() + ": " })).add(
									$("<div>", { class: "col-lg-7 text-left" }).html(
										$("<p>").html(value)))));
							}
							$(".feedbacks-item-keys" + counter).append(
								$("<div>", { class: "row" }).html(
								$("<div>", { class: "col-lg-5 text-right" }).html(
									$("<p>", { text: "SUBMITTED BY: " })).add(
								$("<div>", { class: "col-lg-7 text-left" }).html(
									$("<p>").html(data.feedbacks[i].username)))));
							$(".feedbacks-item-content" + counter).append(
								$("<button>", { class: "btn btn-sm btn-success", onclick: "approveFeedback(this, '"+data.feedbacks[i].id+"');", text: "Approve" }).add(
								$("<button>", { class: "btn btn-sm btn-danger", onclick: "disapproveFeedback(this, '"+data.feedbacks[i].id+"');", text: "Disapprove"})))
						}
					}
				}
				catch (err){

				}
			}
		},
		error: function (){
			$("#for-review").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load submissions." })));
		}
	});
}

function loadApprovedFeedbacks(){
	$("#approved-feedback").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Submissions" })));
	currentRequest = $.ajax({
		url: "/feedback?ajax=1&status=APPROVED",
		success: function (data){
			if(data){
				try{
					if(data.feedbacks.length == 0){
						$("#approved-feedback").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No approved user submissions." })));
					}
					else{
						$("#approved-feedback").html($("<div>", { class: "feedbacks-list col-lg-12", id: "approved-feedbacks-list" }))
						var counter = 0;
						for(i=0;i<data.feedbacks.length;i++){
							counter += 1;
							$("#approved-feedbacks-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "feedbacks-item feedbacks-item"+counter+" col-lg-12" }).html(
										$("<div>", { class: "feedbacks-item-keys feedbacks-item-keys"+counter+" col-lg-9" }).add(
										$("<div>", { class: "feedbacks-item-content feedbacks-item-content"+counter+" col-lg-3 text-right" })))).add(
								$("<hr>")));

							for (var key in data.feedbacks[i].additional_data) {
								if(key == "id" || key == "type"){
									continue
								}
								var value = data.feedbacks[i].additional_data[key];
								if(key == "file"){
									key = "file";
									value = $("<a>", { href: value.file_url, target: "_blank", text: data.feedbacks[i].additional_data["file"]["file_name"] })
								}
								$(".feedbacks-item-keys" + counter).append(
									$("<div>", { class: "row" }).html(
									$("<div>", { class: "col-lg-5 text-right" }).html(
										$("<p>", { text: key.split('_').join(' ').toUpperCase() + ": " })).add(
									$("<div>", { class: "col-lg-7 text-left" }).html(
										$("<p>").html(value)))));
							}
							$(".feedbacks-item-keys" + counter).append(
								$("<div>", { class: "row" }).html(
								$("<div>", { class: "col-lg-5 text-right" }).html(
									$("<p>", { text: "SUBMITTED BY: " })).add(
								$("<div>", { class: "col-lg-7 text-left" }).html(
									$("<p>").html(data.feedbacks[i].username)))));
						}
					}
				}
				catch (err){

				}
			}
		},
		error: function (){
			$("#approved-feedback").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load submissions." })));
		}
	});
}

function loadDisapprovedFeedbacks(){
	$("#disapproved-feedback").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Submissions" })));
	currentRequest = $.ajax({
		url: "/feedback?ajax=1&status=DISAPPROVED",
		success: function (data){
			if(data){
				try{
					if(data.feedbacks.length == 0){
						$("#disapproved-feedback").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No disapproved user submissions." })));
					}
					else{
						$("#disapproved-feedback").html($("<div>", { class: "feedbacks-list col-lg-12", id: "disapproved-feedbacks-list" }))
						var counter = 0;
						for(i=0;i<data.feedbacks.length;i++){
							counter += 1;
							$("#disapproved-feedbacks-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "feedbacks-item feedbacks-item"+counter+" col-lg-12" }).html(
										$("<div>", { class: "feedbacks-item-keys feedbacks-item-keys"+counter+" col-lg-9" }).add(
										$("<div>", { class: "feedbacks-item-content feedbacks-item-content"+counter+" col-lg-3 text-right" })))).add(
								$("<hr>")));

							for (var key in data.feedbacks[i].additional_data) {
								if(key == "id" || key == "type"){
									continue
								}
								var value = data.feedbacks[i].additional_data[key];
								if(key == "file"){
									key = "file";
									value = $("<a>", { href: value.file_url, target: "_blank", text: data.feedbacks[i].additional_data["file"]["file_name"] })
								}
								$(".feedbacks-item-keys" + counter).append(
									$("<div>", { class: "row" }).html(
									$("<div>", { class: "col-lg-5 text-right" }).html(
										$("<p>", { text: key.split('_').join(' ').toUpperCase() + ": " })).add(
									$("<div>", { class: "col-lg-7 text-left" }).html(
										$("<p>").html(value)))));
							}
							$(".feedbacks-item-keys" + counter).append(
								$("<div>", { class: "row" }).html(
								$("<div>", { class: "col-lg-5 text-right" }).html(
									$("<p>", { text: "SUBMITTED BY: " })).add(
								$("<div>", { class: "col-lg-7 text-left" }).html(
									$("<p>").html(data.feedbacks[i].username)))));
						}
					}
				}
				catch (err){

				}
			}
		},
		error: function (){
			$("#disapproved-feedback").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load submissions." })));
		}
	});
}

function approveFeedback(obj, f_id){
	$(obj).prop("disabled", true);
	$.ajax({
		type: "POST",
		url: "/feedback",
		data: {feedback_id: f_id, action: "approve"},
		success: function(data){
			$(obj).prop("disabled", false);
			if($(obj).closest("div.row").parent("div").children("div.row").length == 1){
				$("#for-review").html(
					$("<h3>", { class: "text-center" }).html(
						$("<i>", { class: "fa fa-2x fa-times" })).add(
					$("<h4>", { class: "text-center", text: "No pending user submissions." })));
			}
			else{
				$(obj).closest("div.row").next("hr").remove();
				$(obj).closest("div.row").remove();
			}
		},
		error: function (){
			$(obj).prop("disabled", false);
		}
	});
}

function disapproveFeedback(obj, f_id){
	$(obj).prop("disabled", true);
	$.ajax({
		type: "POST",
		url: "/feedback",
		data: {feedback_id: f_id, action: "disapprove"},
		success: function(data){
			$(obj).prop("disabled", false);
			if($(obj).closest("div.row").parent("div").children("div.row").length == 1){
				$("#for-review").html(
					$("<h3>", { class: "text-center" }).html(
						$("<i>", { class: "fa fa-2x fa-times" })).add(
					$("<h4>", { class: "text-center", text: "No pending user submissions." })));
			}
			else{
				$(obj).closest("div.row").next("hr").remove();
				$(obj).closest("div.row").remove();
			}
		},
		error: function (){
			$(obj).prop("disabled", false);
		}
	});
}