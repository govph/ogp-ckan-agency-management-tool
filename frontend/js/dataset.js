var currentRequest = undefined;

$(document).ready(function (){
	loadForReviewDataset();
	loadLogs();
	$("#for-review-search").focus();
});

$(function(){
	$("#for-review-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadForReviewDataset();
		$("#for-review-search").focus();
	});
	$("#sent-back-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadSentBackDataset();
		$("#sent-back-search").focus();
	});
	$("#for-clean-up-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadForCleanUpDataset();
		$("#for-clean-up-search").focus();
	});
	$("#published-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadPublishedDataset();
		$("#published-search").focus();
	});
	$("#flagged-for-deletion-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadForDeletionDataset();
		$("#flagged-for-deletion-search").focus();
	});
	$("#for-review-order").on("change", function (){
		currentRequest.abort();
		loadForReviewDataset(this.value);
	});
	$("#sent-back-order").on("change", function (){
		currentRequest.abort();
		loadSentBackDataset(this.value);
	});
	$("#for-clean-up-order").on("change", function (){
		currentRequest.abort();
		loadForCleanUpDataset(this.value);
	});
	$("#published-order").on("change", function (){
		currentRequest.abort();
		loadPublishedDataset(this.value);
	});
	$("#flagged-for-deletion-order").on("change", function (){
		currentRequest.abort();
		loadForDeletionDataset(this.value);
	});
	$("#for-review-search-form").submit(function (e){
		searchDataset($(this).find("input").val(), this, "FOR REVIEW");
		e.preventDefault();
	});
	$("#sent-back-search-form").submit(function (e){
		searchDataset($(this).find("input").val(), this, "SENT BACK");
		e.preventDefault();
	});
	$("#for-clean-up-search-form").submit(function (e){
		searchDataset($(this).find("input").val(), this, "FOR CLEAN UP");
		e.preventDefault();
	});
	$("#published-search-form").submit(function (e){
		searchDataset($(this).find("input").val(), this, "PUBLISHED");
		e.preventDefault();
	});
	$("#flagged-for-deletion-search-form").submit(function (e){
		searchDataset($(this).find("input").val(), this, "FLAGGED FOR DELETION");
		e.preventDefault();
	});
});

function loadForReviewDataset(order){
	$("#for-review-search").val("");
	$("#for-review-dataset-list").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Datasets" })));
	var url = "/api/v1/data?status=FOR%20REVIEW&type=DATASET"
	if(order){
		url += "&order=" + order;
	}
	currentRequest = $.ajax({
		url: url,
		success: function (data){
			if(data){
				try{
					if(data.data.length == 0){
						$("#for-review-dataset-list").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No for review datasets found." })));
					}
					else{
						$("#for-review-search, #for-review-search-btn, #for-review-order").prop("disabled", false);
						$("#for-review-dataset-list").empty();
						var counter = 0;
						for(i=0;i<data.data.length;i++){
							counter += 1;
							var file_type = "",
							createdDate = new Date(data.data[i].created);
							createdDate = [(createdDate.getMonth() + 1), createdDate.getDate(), createdDate.getFullYear()].join("-");
							try {
								file_type = data.data[i].filename.split('.').pop();
							}
							catch (error){
								console.log("no file");
							}
							$("#for-review-dataset-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "dataset-items col-lg-12", "data-link": "/dataset/" + data.data[i].id }).html(
										$("<div>", { class: "dataset-icons col-lg-1" }).html(
											$("<img>", { class: "img-responsive", src: "/images/dataset-icn.png" }).add(
											$("<label>", { class: "label label-block label-success text-uppercase", text: "FILE"}))).add(
										$("<div>", { class: "dataset-item-content feedbacks-item-content"+counter+" col-lg-11" }).html(
											$("<div>", { class: "row"}).html(
												$("<div>", { class: "col-lg-8" }).html(
													$("<p>", { class: "dataset-title", text: data.data[i].dataset_title })).add(
												$("<div>", { class: "col-lg-2 no-padding" }).html(
													$("<label>", { class: "label label-primary", text: "FOR REVIEW" }))).add(
												$("<div>", { class: "col-lg-2 no-padding text-center" }).html(
													$("<p>", { class: "dashboard-dataset-date", title: data.data[i].created, rel: "tooltip", text: " " + createdDate }).prepend($("<i>", { class: "fa fa-fw fa-calendar-o" }))))).add(
											$("<p>", { class: "dataset-description", text: data.data[i].dataset_description })).add(
											$("<p>", { class: "dataset-author", text: "Submitted By: " }).append($("<span>", { text: data.data[i].department })))))
										// 	.add(
										// $("<div>", { class: "col-lg-2 dataset-action-buttons no-padding text-center"}).html(
										// 	$("<i>", { class: "fa fa-fw fa-calendar-o" }).add(
										// 	$("<strong>", { text: data.data[i].created }))))
											)).add(
								$("<hr>")));
						}
						$(".dataset-items").click(function (){
							window.location.href = $(this).data("link");
						});
						$("[rel=tooltip]").tooltip();
						$("#for-review-dataset-list").find("hr:last-child").remove();
						$("#for-review-search").focus();
					}
				}
				catch (err){
					console.log(err);
				}
			}
		},
		error: function (){
			$("#for-review-dataset-list").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load datasets." })));
		}
	});
}

function loadSentBackDataset(order){
	$("#sent-back-dataset-list").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Datasets" })));
	var url = "/api/v1/data?status=SENT%20BACK&type=DATASET";
	if(order){
		url += "&order=" + order;
	}
	currentRequest = $.ajax({
		url: url,
		success: function (data){
			if(data){
				try{
					if(data.data.length == 0){
						$("#sent-back-dataset-list").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No sent back datasets found." })));
					}
					else{
						$("#sent-back-search, #sent-back-search-btn, #sent-back-order").prop("disabled", false);
						$("#sent-back-dataset-list").empty();
						var counter = 0;
						for(i=0;i<data.data.length;i++){
							counter += 1;
							var file_type = "",
							createdDate = new Date(data.data[i].created);
							createdDate = [(createdDate.getMonth() + 1), createdDate.getDate(), createdDate.getFullYear()].join("-");
							try {
								file_type = data.data[i].filename.split('.').pop();
							}
							catch (error){
								console.log("no file");
							}
							$("#sent-back-dataset-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "dataset-items col-lg-12", "data-link": "/dataset/" + data.data[i].id }).html(
										$("<div>", { class: "dataset-icons col-lg-1" }).html(
											$("<img>", { class: "img-responsive", src: "/images/dataset-icn.png" }).add(
											$("<label>", { class: "label label-block label-success text-uppercase", text: "FILE"}))).add(
										$("<div>", { class: "dataset-item-content feedbacks-item-content"+counter+" col-lg-11" }).html(
											$("<div>", { class: "row"}).html(
												$("<div>", { class: "col-lg-8" }).html(
													$("<p>", { class: "dataset-title", text: data.data[i].dataset_title })).add(
												$("<div>", { class: "col-lg-2 no-padding" }).html(
													$("<label>", { class: "label label-danger", text: "SENT BACK" }))).add(
												$("<div>", { class: "col-lg-2 no-padding text-center" }).html(
													$("<p>", { class: "dashboard-dataset-date", text: " " + createdDate }).prepend($("<i>", { class: "fa fa-fw fa-calendar-o" }))))).add(
											$("<p>", { class: "dataset-description", text: data.data[i].dataset_description })).add(
											$("<p>", { class: "dataset-author", text: "Submitted By: " }).append($("<span>", { text: data.data[i].department }))).add(
											$("<p>", { class: "dataset-submitted", text: "Submitted On: " }).append($("<span>", { text: data.data[i].created })))))
										// 	.add(
										// $("<div>", { class: "col-lg-2 dataset-action-buttons no-padding text-center"}).html(
										// 	$("<i>", { class: "fa fa-fw fa-calendar-o" }).add(
										// 	$("<strong>", { text: data.data[i].created }))))
											)).add(
								$("<hr>")));
						}
						$(".dataset-items").click(function (){
							window.location.href = $(this).data("link");
						});
						$("#sent-back-dataset-list").find("hr:last-child").remove();
						$("#sent-back-search").focus();
					}
				}
				catch (err){
					console.log(err);
				}
			}
		},
		error: function (){
			$("#sent-back-dataset-list").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load datasets." })));
		}
	});
}

function loadForCleanUpDataset(order){
	$("#for-clean-up-dataset-list").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Datasets" })));
	var url = "/api/v1/data?status=FOR%20CLEAN%20UP&type=DATASET";
	if(order){
		url += "&order=" + order;
	}
	currentRequest = $.ajax({
		url: url,
		success: function (data){
			if(data){
				try{
					if(data.data.length == 0){
						$("#for-clean-up-dataset-list").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No for clean up datasets found." })));
					}
					else{
						$("#for-clean-up-search, #for-clean-up-search-btn, #for-clean-up-order").prop("disabled", false);
						$("#for-clean-up-dataset-list").empty();
						var counter = 0;
						for(i=0;i<data.data.length;i++){
							counter += 1;
							var file_type = "",
							createdDate = new Date(data.data[i].created);
							createdDate = [(createdDate.getMonth() + 1), createdDate.getDate(), createdDate.getFullYear()].join("-");
							try {
								file_type = data.data[i].filename.split('.').pop();
							}
							catch (error){
								console.log("no file");
							}
							$("#for-clean-up-dataset-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "dataset-items col-lg-12", "data-link": "/dataset/" + data.data[i].id }).html(
										$("<div>", { class: "dataset-icons col-lg-1" }).html(
											$("<img>", { class: "img-responsive", src: "/images/dataset-icn.png" }).add(
											$("<label>", { class: "label label-block label-success text-uppercase", text: "FILE"}))).add(
										$("<div>", { class: "dataset-item-content feedbacks-item-content"+counter+" col-lg-11" }).html(
											$("<div>", { class: "row"}).html(
												$("<div>", { class: "col-lg-8" }).html(
													$("<p>", { class: "dataset-title", text: data.data[i].dataset_title })).add(
												$("<div>", { class: "col-lg-2 no-padding" }).html(
													$("<label>", { class: "label label-warning", text: "FOR CLEAN UP" }))).add(
												$("<div>", { class: "col-lg-2 no-padding text-center" }).html(
													$("<p>", { class: "dashboard-dataset-date", text: " " + createdDate }).prepend($("<i>", { class: "fa fa-fw fa-calendar-o" }))))).add(
											$("<p>", { class: "dataset-description", text: data.data[i].dataset_description })).add(
											$("<p>", { class: "dataset-author", text: "Submitted By: " }).append($("<span>", { text: data.data[i].department }))).add(
											$("<p>", { class: "dataset-submitted", text: "Submitted On: " }).append($("<span>", { text: data.data[i].created })))))
										// 	.add(
										// $("<div>", { class: "col-lg-2 dataset-action-buttons no-padding text-center"}).html(
										// 	$("<i>", { class: "fa fa-fw fa-calendar-o" }).add(
										// 	$("<strong>", { text: data.data[i].created }))))
											)).add(
								$("<hr>")));
						}
						$(".dataset-items").click(function (){
							window.location.href = $(this).data("link");
						});
						$("#for-clean-up-dataset-list").find("hr:last-child").remove();
						$("#for-clean-up-search").focus();
					}
				}
				catch (err){
					console.log(err);
				}
			}
		},
		error: function (){
			$("#for-clean-up-dataset-list").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load datasets." })));
		}
	});
}

function loadPublishedDataset(order){
	$("#published-dataset-list").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Datasets" })));
	var url = "/api/v1/data?status=PUBLISHED&type=DATASET";
	if(order){
		url += "&order=" + order;
	}
	currentRequest = $.ajax({
		url: url,
		success: function (data){
			if(data){
				try{
					if(data.data.length == 0){
						$("#published-dataset-list").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No published datasets found." })));
					}
					else{
						$("#published-search, #published-search-btn, #published-order").prop("disabled", false);
						$("#published-dataset-list").empty();
						var counter = 0;
						for(i=0;i<data.data.length;i++){
							counter += 1;
							var file_type = "",
							createdDate = new Date(data.data[i].created);
							createdDate = [(createdDate.getMonth() + 1), createdDate.getDate(), createdDate.getFullYear()].join("-");
							try {
								file_type = data.data[i].filename.split('.').pop();
							}
							catch (error){
								console.log("no file");
							}
							$("#published-dataset-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "dataset-items col-lg-12", "data-link": "/dataset/" + data.data[i].id }).html(
										$("<div>", { class: "dataset-icons col-lg-1" }).html(
											$("<img>", { class: "img-responsive", src: "/images/dataset-icn.png" }).add(
											$("<label>", { class: "label label-block label-success text-uppercase", text: "FILE"}))).add(
										$("<div>", { class: "dataset-item-content feedbacks-item-content"+counter+" col-lg-11" }).html(
											$("<div>", { class: "row"}).html(
												$("<div>", { class: "col-lg-8" }).html(
													$("<p>", { class: "dataset-title", text: data.data[i].dataset_title })).add(
												$("<div>", { class: "col-lg-2 no-padding" }).html(
													$("<label>", { class: "label label-info", text: "PUBLISHED" }))).add(
												$("<div>", { class: "col-lg-2 no-padding text-center" }).html(
													$("<p>", { class: "dashboard-dataset-date", text: " " + createdDate }).prepend($("<i>", { class: "fa fa-fw fa-calendar-o" }))))).add(
											$("<p>", { class: "dataset-description", text: data.data[i].dataset_description })).add(
											$("<p>", { class: "dataset-author", text: "Submitted By: " }).append($("<span>", { text: data.data[i].department }))).add(
											$("<p>", { class: "dataset-submitted", text: "Submitted On: " }).append($("<span>", { text: data.data[i].created })))))
										// 	.add(
										// $("<div>", { class: "col-lg-2 dataset-action-buttons no-padding text-center"}).html(
										// 	$("<i>", { class: "fa fa-fw fa-calendar-o" }).add(
										// 	$("<strong>", { text: data.data[i].created }))))
											)).add(
								$("<hr>")));
						}
						$(".dataset-items").click(function (){
							window.location.href = $(this).data("link");
						});
						$("#published-dataset-list").find("hr:last-child").remove();
						$("#published-search").focus();
					}
				}
				catch (err){
					console.log(err);
				}
			}
		},
		error: function (){
			$("#published-dataset-list").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load datasets." })));
		}
	});
}

function loadForDeletionDataset(order){
	$("#flagged-for-deletion-dataset-list").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Datasets" })));
	var url = "/api/v1/data?status=FLAGGED%20FOR%20DELETION&type=DATASET";
	if(order){
		url += "&order=" + order;
	}
	currentRequest = $.ajax({
		url: url,
		success: function (data){
			if(data){
				try{
					if(data.data.length == 0){
						$("#flagged-for-deletion-dataset-list").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No flagged for deletion datasets found." })));
					}
					else{
						$("#flagged-for-deletion-search, #flagged-for-deletion-search-btn, #flagged-for-deletion-order").prop("disabled", false);
						$("#flagged-for-deletion-dataset-list").empty();
						var counter = 0;
						for(i=0;i<data.data.length;i++){
							counter += 1;
							var file_type = "",
							createdDate = new Date(data.data[i].created);
							createdDate = [(createdDate.getMonth() + 1), createdDate.getDate(), createdDate.getFullYear()].join("-");
							try {
								file_type = data.data[i].filename.split('.').pop();
							}
							catch (error){
								console.log("no file");
							}
							$("#flagged-for-deletion-dataset-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "dataset-items col-lg-12", "data-link": "/dataset/" + data.data[i].id }).html(
										$("<div>", { class: "dataset-icons col-lg-1" }).html(
											$("<img>", { class: "img-responsive", src: "/images/dataset-icn.png" }).add(
											$("<label>", { class: "label label-block label-success text-uppercase", text: "FILE"}))).add(
										$("<div>", { class: "dataset-item-content feedbacks-item-content"+counter+" col-lg-11" }).html(
											$("<div>", { class: "row"}).html(
												$("<div>", { class: "col-lg-8" }).html(
													$("<p>", { class: "dataset-title", text: data.data[i].dataset_title })).add(
												$("<div>", { class: "col-lg-2 no-padding" }).html(
													$("<label>", { class: "label label-inverse", text: "FLAGGED FOR DELETION" }))).add(
												$("<div>", { class: "col-lg-2 no-padding text-center" }).html(
													$("<p>", { class: "dashboard-dataset-date", text: " " + createdDate }).prepend($("<i>", { class: "fa fa-fw fa-calendar-o" }))))).add(
											$("<p>", { class: "dataset-description", text: data.data[i].dataset_description })).add(
											$("<p>", { class: "dataset-author", text: "Submitted By: " }).append($("<span>", { text: data.data[i].department }))).add(
											$("<p>", { class: "dataset-submitted", text: "Submitted On: " }).append($("<span>", { text: data.data[i].created })))))
										// 	.add(
										// $("<div>", { class: "col-lg-2 dataset-action-buttons no-padding text-center"}).html(
										// 	$("<i>", { class: "fa fa-fw fa-calendar-o" }).add(
										// 	$("<strong>", { text: data.data[i].created }))))
											)).add(
								$("<hr>")));
						}
						$(".dataset-items").click(function (){
							window.location.href = $(this).data("link");
						});
						$("#flagged-for-deletion-dataset-list").find("hr:last-child").remove();
						$("#flagged-for-deletion-search").focus();
					}
				}
				catch (err){
					console.log(err);
				}
			}
		},
		error: function (){
			$("#flagged-for-deletion-dataset-list").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load datasets." })));
		}
	});
}

function loadLogs(){
	$.ajax({
		url: "/logs",
		success: function(data){
			$("#dashboard-updates").empty();
			if(data){
				if(data.logs.length > 0){
					for(i=0;i<data.logs.length;i++){
						$("#dashboard-updates").append($("<div>", { class: "row" }).html(
							$("<div>", { class: "col-lg-1" }).html(
								$("<span>", { class: "fa-stack" }).html(
									$("<i>", { class: "fa fa-square fa-stack-2x text-" + data.logs[i].color }).add(
									$("<i>", { class: "fa fa-"+data.logs[i].icon+" fa-stack-1x fa-inverse"})))).add(
							$("<div>", { class: "col-lg-10" }).html(
								$("<p>", { text: data.logs[i].action }).add(
								$("<p>").html(
									$("<i>", { class: "fa fa-fw fa-calendar-o"}).add(
									$("<time>", { class: "timeago", datetime: data.logs[i].created_time_timeago }))))))).add($("<hr>")));
					}
					$("#dashboard-updates").find("hr:last-child").remove();
					jQuery("time.timeago").timeago();
					return
				}
			}
			$("#dashboard-updates").html($("<h4>", { class: "text-center" }).html(
				$("<span>", { class: "fa-stack" }).html(
					$("<i>", { class: "fa fa-circle fa-stack-2x" }).add(
					$("<i>", { class: "fa fa-info fa-stack-1x fa-inverse"}))).add(
				$("<p>", { text: "No recent updates."}))));
		},
		error: function (){

		}
	});
}

function searchDataset(query, form, status){
	$(form).find("input").prop("disabled", true);
	$(form).find("button:submit").prop("disabled", true);
	$(form).parent("div").next("div").children("select").prop("disabled", true).val("");
	$(form).closest(".row").next(".row").children(".dashboard-datasets-list").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Datasets" })));
	var url = "/dashboard?ajax=1&query=" + query + "&status=" + status
	currentRequest = $.ajax({
		url: url,
		success: function (data){
			if(data){
				try{
					if(data.data.length == 0){
						$(form).find("input").prop("disabled", false);
						$(form).find("button:submit").prop("disabled", false);
						$(form).closest(".row").next(".row").children(".dashboard-datasets-list").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No result found." })));
						$(form).find("input").focus();
					}
					else{
						$(form).find("input").prop("disabled", false);
						$(form).find("button:submit").prop("disabled", false);
						$(form).parent("div").next("div").children("select").prop("disabled", false);
						$(form).closest(".row").next(".row").children(".dashboard-datasets-list").html(
							$("<div>", { class: "row" }).html(
								$("<div>", { class: "col-lg-12" }).html(
									$("<div>", { class: "alert alert-info", text: " Showing results found for " }).prepend(
										$("<i>", { class: "fa fa-fw fa-info" })).append($("<strong>", { text: query + "." })))));
						var counter = 0;
						for(i=0;i<data.data.length;i++){
							counter += 1;
							var file_type = "",
							datasetStatusClass="",
							createdDate = new Date(data.data[i].created);
							createdDate = [(createdDate.getMonth() + 1), createdDate.getDate(), createdDate.getFullYear()].join("-");
							try {
								file_type = data.data[i].filename.split('.').pop();
							}
							catch (error){
								console.log("no file");
							}
							if (data.data[i].status == "FOR REVIEW"){
								datasetStatusClass = "label-primary";
							}
							else if (data.data[i].status == "FOR CLEAN UP"){
								datasetStatusClass = "label-warning";
							}
							else if (data.data[i].status == "PUBLISHED"){
								datasetStatusClass = "label-info";
							}
							else if (data.data[i].status == "FLAGGED FOR DELETION"){
								datasetStatusClass = "label-inverse";
							}
							else if (data.data[i].status == "SENT BACK"){
								datasetStatusClass = "label-danger";
							}
							$(form).closest(".row").next(".row").children(".dashboard-datasets-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "dataset-items col-lg-12", "data-link": "/dataset/" + data.data[i].id }).html(
										$("<div>", { class: "dataset-icons col-lg-1" }).html(
											$("<img>", { class: "img-responsive", src: "/images/dataset-icn.png" }).add(
											$("<label>", { class: "label label-block label-success text-uppercase", text: "FILE"}))).add(
										$("<div>", { class: "dataset-item-content feedbacks-item-content"+counter+" col-lg-11" }).html(
											$("<div>", { class: "row"}).html(
												$("<div>", { class: "col-lg-8" }).html(
													$("<p>", { class: "dataset-title", text: data.data[i].dataset_title })).add(
												$("<div>", { class: "col-lg-2 no-padding" }).html(
													$("<label>", { class: "label "+datasetStatusClass, text: data.data[i].status }))).add(
												$("<div>", { class: "col-lg-2 no-padding text-center" }).html(
													$("<p>", { class: "dashboard-dataset-date", title: data.data[i].created, rel: "tooltip", text: " " + createdDate }).prepend($("<i>", { class: "fa fa-fw fa-calendar-o" }))))).add(
											$("<p>", { class: "dataset-description", text: data.data[i].dataset_description })).add(
											$("<p>", { class: "dataset-author", text: "Submitted By: " }).append($("<span>", { text: data.data[i].department })))))
										// 	.add(
										// $("<div>", { class: "col-lg-2 dataset-action-buttons no-padding text-center"}).html(
										// 	$("<i>", { class: "fa fa-fw fa-calendar-o" }).add(
										// 	$("<strong>", { text: data.data[i].created }))))
											)).add(
								$("<hr>")));
						}
						$(".dataset-items").click(function (){
							window.location.href = $(this).data("link");
						});
						$("[rel=tooltip]").tooltip();
						$(form).closest(".row").next(".row").children(".dashboard-datasets-list").find("hr:last-child").remove();
						$(form).find("input").focus();
					}
				}
				catch (err){
					console.log(err);
				}
			}
		},
		error: function (){
			$(form).find("input").prop("disabled", false);
			$(form).find("button:submit").prop("disabled", false);
			$(form).closest(".row").next(".row").children(".dashboard-datasets-list").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load datasets." })));
		}
	});
}