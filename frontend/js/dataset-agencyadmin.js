var currentRequest = undefined;

$(document).ready(function (){
	loadUserDataset();
	$("#dataset-search-form").submit(function (e){
		searchDataset($(this).find("input").val());
		e.preventDefault();
	});
});

$(function(){
	$("#user-dataset-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadUserDataset();
	});
	$("#activity-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadActivities();
	});
	$("#dataset-filter").on("change", function (){
		currentRequest.abort();
		loadUserDataset(this.value);
	});
	$("#activity-filter").on("change", function (){
		currentRequest.abort();
		loadActivities(this.value);
	});
	$("#dataset-order").on("change", function (){
		currentRequest.abort();
		loadUserDataset("", this.value);
	});
});

function loadUserDataset(filter, order){
	$("#user-dataset-dataset-list").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Datasets" })));
	$("#dataset-search-form").find("input").prop("disabled", true).val("");
	$("#dataset-search-form").find("button").prop("disabled", true);
	$("#dataset-filter, #dataset-order").prop("disabled", true);
	if($.inArray(filter, ["FOR REVIEW", "SENT BACK", "FOR CLEAN UP", "PUBLISHED", "FLAGGED FOR DELETION"]) !== -1){
		var url = "/api/v1/data?uacs_id="+uacsID+"&type=DATASET&status=" + filter;
	}
	else{
		var url = "/api/v1/data?uacs_id="+uacsID+"&type=DATASET";
	}

	if(order){
		url += "&order=" + order;
	}
	currentRequest = $.ajax({
		url: url,
		success: function (data){
			if(data){
				renderDatasets(data);
			}
		},
		error: function (){
			$("#user-dataset-dataset-list").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load datasets." })));
		}
	});
}

function loadActivities(filter){
	$("#dashboard-updates").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Activities" })));
	if(filter === undefined || filter == "ALL"){
		var url = "/logs";
	}
	else{
		var url = "/logs";
	}
	currentRequest = $.ajax({
		url: url,
		success: function (data){
			if(data){
				$("#activities-filter").prop("disabled", false);
				$("#dashboard-updates").empty();
				if(data.logs.length > 0){
					for(i=0;i<data.logs.length;i++){
						$("#dashboard-updates").append($("<div>", { class: "row" }).html(
							$("<div>", { class: "col-lg-12" }).html(
								$("<div>", { class: "pull-left" }).html(
								$("<span>", { class: "fa-stack" }).html(
									$("<i>", { class: "fa fa-square fa-stack-2x text-" + data.logs[i].color }).add(
									$("<i>", { class: "fa fa-"+data.logs[i].icon+" fa-stack-1x fa-inverse"})))).add(
								$("<div>", { class: "activity-content" }).html(
									$("<p>", { text: data.logs[i].action }).add($("<i>", { class: "fa fa-fw fa-calendar-o"})).add(
								$("<time>", { class: "timeago", datetime: data.logs[i].created_time_timeago }))).add($("<hr>"))))));
					}
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

function searchDataset(query){
	$("#user-dataset-dataset-list").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Datasets" })));
	$("#dataset-search-form").find("input").prop("disabled", true);
	$("#dataset-search-form").find("button").prop("disabled", true);
	$("#dataset-filter, #dataset-order").prop("disabled", true);
	var url = "/dashboard?ajax=1&query=" + query + "&status=" + status

	// if(order){
	// 	url += "&order=" + order;
	// }
	currentRequest = $.ajax({
		url: url,
		success: function (data){
			if(data){
				renderDatasets(data, "", query);
			}

		},
		error: function (){
			$("#user-dataset-dataset-list").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load datasets." })));
		}
	});
}

function renderDatasets(datasets, filter, search){
	try{
		if(datasets.data.length == 0){
			var label = "No datasets found.";
			if(filter && filter != "ALL"){
				label = "No " + filter.toLowerCase() + " datasets found.";
			}
			if(search){
				$("#dataset-search-form").find("input").prop("disabled", false);
				$("#dataset-search-form").find("button:submit").prop("disabled", false);
				$("#dataset-search-form").find("input").focus();
			}
			$("#user-dataset-dataset-list").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-times" })).add(
				$("<h4>", { class: "text-center", text: label })));
			$("#dataset-filter").prop("disabled", false);

		}
		else{
			if(search){
				$("#user-dataset-dataset-list").html(
					$("<div>", { class: "row" }).html(
						$("<div>", { class: "col-lg-12" }).html(
							$("<div>", { class: "alert alert-info", text: " Showing results found for " }).prepend(
								$("<i>", { class: "fa fa-fw fa-info" })).append($("<strong>", { text: search + "." })))))
			}
			else{
				$("#user-dataset-dataset-list").empty();
			}
			$("#dataset-search-form").find("input").prop("disabled", false);
			$("#dataset-search-form").find("button:submit").prop("disabled", false);
			$("#dataset-filter, #dataset-order").prop("disabled", false);
			var counter = 0;
			for(i=0;i<datasets.data.length;i++){
				counter += 1;
				var file_type = "",
				datasetStatusClass = "",
				note = "",
				fileCount = 0,
				createdDate = new Date(datasets.data[i].created);
				createdDate = [(createdDate.getMonth() + 1), createdDate.getDate(), createdDate.getFullYear()].join("-");

				if (datasets.data[i].status == "FOR REVIEW"){
					datasetStatusClass = "label-primary";
				}
				else if (datasets.data[i].status == "FOR CLEAN UP"){
					datasetStatusClass = "label-warning";
				}
				else if (datasets.data[i].status == "PUBLISHED"){
					datasetStatusClass = "label-info";
				}
				else if (datasets.data[i].status == "FLAGGED FOR DELETION"){
					datasetStatusClass = "label-inverse";
				}
				else if (datasets.data[i].status == "SENT BACK"){
					datasetStatusClass = "label-danger";
					try {
						console.log(datasets.data[i])
						var template = '<div class="popover popover-note" role="tooltip"><div class="arrow arrow-note"></div><h3 class="popover-title popover-note-title"></h3><div class="popover-content popover-note-content"></div></div>';
						var comment = datasets.data[i].comment[0].comment,
						comment_date = datasets.data[i].comment[0].comment_date.split(" "),
						comment_author = datasets.data[i].comment[0].comment_author;
						comment_date = comment_date[0] + " " + comment_date[1] + " " + comment_date[2];
						note = $("<span>", { class: "dashboard-dataset-note", "data-toggle": "popover", title: "COMMENTS", "data-content": "<span><i class='fa fa-fw fa-comment'></i> Posted on <strong>"+ comment_date +"</strong> by <strong>"+ comment_author +"</strong></span><hr><p>"+comment+"</p>", "data-trigger": "hover", "data-container": "body", "data-html": true, "data-placement": "left", "data-template": template }).html($("<i>", { class: "fa fa-fw fa-comment" })).append(" NOTE")
					}
					catch (e){
						console.log(e);
					}
				}
				// try {
				// 	file_type = $.ajax({
				// 		url: "/api/v1/data?dataset_id="+data.data[i].id+"&type=RESOURCE",
				// 		success: function (data){
				// 			console.log(data)
				// 			return data.data.additional_data["file"]
				// 		}
				// 	})
				// 	console.log(file_type)
				// 	file_type = data.data[i].filename.split('.').pop();
				// }
				// catch (error){
				// 	console.log(error)
				// 	console.log("no file");
				// }
				$("#user-dataset-dataset-list").append(
					$("<div>", { class: "row" }).html(
						$("<div>", { class: "dataset-items col-lg-12", "data-link": "/dataset/" + datasets.data[i].id }).html(
							$("<div>", { class: "dataset-icons col-lg-1" }).html(
								$("<img>", { class: "img-responsive", src: "/images/dataset-icn.png" }).add(
								$("<label>", { class: "label label-block label-success text-uppercase", text: "FILE"}))).add(
							$("<div>", { class: "dataset-item-content feedbacks-item-content"+counter+" col-lg-11 no-padding-left" }).html(
								$("<div>", { class: "row"}).html(
									$("<div>", { class: "col-lg-8" }).html(
										$("<p>", { class: "dataset-title", text: datasets.data[i].dataset_title })).add(
									$("<div>", { class: "col-lg-2 no-padding" }).html(
										$("<label>", { class: "label " + datasetStatusClass, text: datasets.data[i].status }).add(note))).add(
									$("<div>", { class: "col-lg-2 no-padding text-center" }).html(
										$("<p>", { class: "dashboard-dataset-date", text: " " + createdDate }).prepend($("<i>", { class: "fa fa-fw fa-calendar-o" }))))).add(
								$("<p>", { class: "dataset-description", text: datasets.data[i].dataset_description })).add(
								$("<p>", { class: "dataset-author", text: "Submitted by " }).append($("<span>", { text: datasets.data[i].department })))))
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
			$("#user-dataset-dataset-list").find("hr:last-child").remove();
		 	$('[data-toggle="popover"]').popover();
		 	$("#dataset-search-form").find("input").focus();
		}
	}
	catch (err){
		console.log(err);
	}
}