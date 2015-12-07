var currentRequest = undefined;

$(document).ready(function (){
	loadPendingAgencyAdmin();
});

$(function(){
	$("#pending-admin-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadPendingAgencyAdmin();
	});
	$("#approved-admin-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadApprovedAgencyAdmin();
	});
	$("#disapproved-admin-tab").on("shown.bs.tab", function (){
		currentRequest.abort();
		loadDisapprovedAgencyAdmin();
	});
});

function loadPendingAgencyAdmin(){
	$("#pending-admin").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Agency Admin Users" })));
	currentRequest = $.ajax({
		url: "/agency/admins?ajax=1&status=verified",
		success: function (data){
			if(data){
				try{
					if(data.users.length == 0){
						$("#pending-admin").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No pending agency admin users." })));
					}
					else{
						$("#pending-admin").html($("<div>", { class: "feedbacks-list col-lg-12", id: "pending-admin-feedbacks-list" }))
						var counter = 0;
						for(i=0;i<data.users.length;i++){
							counter += 1;
							$("#pending-admin-feedbacks-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "feedbacks-item feedbacks-item"+counter+" col-lg-12" }).html(
										$("<div>", { class: "feedbacks-item-keys col-lg-9" }).html(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "NAME:" })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>", { text: data.users[i].name })))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "MOBILE NUMBER:" })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>", { text: data.users[i].mobile_number }))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "EMAIL:" })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>", { text: data.users[i].email }))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "DEPARTMENT:" })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>", { text: data.users[i].department }))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "AGENCY:" })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>", { text: data.users[i].agency }))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "REGION:" })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>", { text: data.users[i].region }))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "OPERATING UNIT:" })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>", { text: data.users[i].operating_unit }))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "DATE REGISTERED:" })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>", { text: data.users[i].registered })))))).add(
										$("<div>", { class: "feedbacks-item-content col-lg-3 text-right" }).html(
											$("<button>", { class: "btn btn-sm btn-success", onclick: "approveAgencyAdmin(this, '"+data.users[i].id+"');", text: " Approve" }).prepend($("<i>", { class: "fa fa-fw fa-check" })).add(
								$("<button>", { class: "btn btn-sm btn-danger", onclick: "disapproveAgencyAdmin(this, '"+data.users[i].id+"');", text: " Disapprove"}).prepend($("<i>", { class: "fa fa-fw fa-times" }))))))).add(
								$("<hr>")));
						}
					}
				}
				catch (err){
					console.log(err);
				}
			}
		},
		error: function (){
			$("#pending-admin").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load agency admin users." })));
		}
	});
}

function loadApprovedAgencyAdmin(){
	$("#approved-admin").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Agency Admin Users" })));
	currentRequest = $.ajax({
		url: "/agency/admins?ajax=1&status=approved",
		success: function (data){
			if(data){
				try{
					if(data.users.length == 0){
						$("#approved-admin").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No approved agency admin users." })));
					}
					else{
						$("#approved-admin").html($("<div>", { class: "feedbacks-list col-lg-12", id: "approved-admins-list" }))
						for(i=0;i<data.users.length;i++){
							$("#approved-admins-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "feedbacks-item col-lg-12" }).html(
										$("<div>", { class: "feedbacks-item-keys col-lg-9" }).html(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "NAME: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].name)))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "EMAIL: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].email))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "MOBILE NUMBER: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].mobile_number))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "DEPARTMENT: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].department))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "AGENCY: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].agency))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "REGION: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].region))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "OPERATING UNIT: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].operating_unit))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "REGISTERED ON: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].registered))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "APPROVED BY: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].approved_by))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "APPROVED ON: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].approved_on)))))).add(
										$("<div>", { class: "feedbacks-item-content col-lg-3 text-right" }).html(
											$("<button>", { class: "btn btn-sm btn-danger", onclick: "disapproveAgencyAdmin(this, '"+data.users[i].id+"');", text: "Disapprove" }))))).add(
								$("<hr>")));
						}
					}
				}
				catch (err){
					console.log(err)
				}
			}
		},
		error: function (){
			$("#approved-admin").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load agency admin users." })));
		}
	});
}

function loadDisapprovedAgencyAdmin(){
	$("#disapproved-admin").html(
		$("<h3>", { class: "text-center" }).html(
			$("<i>", { class: "fa fa-2x fa-spin fa-circle-o-notch" })).add(
		$("<h4>", { class: "text-center", text: "Loading Agency Admin Users" })));
	currentRequest = $.ajax({
		url: "/agency/admins?ajax=1&status=disapproved",
		success: function (data){
			if(data){
				try{
					if(data.users.length == 0){
						$("#disapproved-admin").html(
							$("<h3>", { class: "text-center" }).html(
								$("<i>", { class: "fa fa-2x fa-times" })).add(
							$("<h4>", { class: "text-center", text: "No disapproved agency admin users." })));
					}
					else{
						$("#disapproved-admin").html($("<div>", { class: "feedbacks-list col-lg-12", id: "disapproved-admins-list" }))
						var counter = 0;
						for(i=0;i<data.users.length;i++){
							counter += 1;
							$("#disapproved-admins-list").append(
								$("<div>", { class: "row" }).html(
									$("<div>", { class: "feedbacks-item col-lg-12" }).html(
										$("<div>", { class: "feedbacks-item-keys col-lg-9" }).html(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "NAME: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].name)))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "EMAIL: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].email))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "MOBILE NUMBER: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].mobile_number))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "DEPARTMENT: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].department))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "AGENCY: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].agency))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "REGION: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].region))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "OPERATING UNIT: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].operating_unit))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "REGISTERED ON: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].registered))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "DISAPPROVED BY: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].disapproved_by))))).add(
											$("<div>", { class: "row" }).html(
												$("<div>", { class: "col-lg-3 text-right" }).html(
													$("<p>", { text: "DISAPPROVED ON: " })).add(
												$("<div>", { class: "col-lg-9 text-left" }).html(
													$("<p>").html(data.users[i].disapproved_on)))))).add(
										$("<div>", { class: "feedbacks-item-content col-lg-3 text-right" }).html(
											$("<button>", { class: "btn btn-sm btn-success", onclick: "approveAgencyAdmin(this, '"+data.users[i].id+"');", text: "Approve" }))))).add(
								$("<hr>")));
						}
					}
				}
				catch (err){

				}
			}
		},
		error: function (){
			$("#disapproved-admin").html(
				$("<h3>", { class: "text-center" }).html(
					$("<i>", { class: "fa fa-2x fa-warning" })).add(
				$("<h4>", { class: "text-center", text: "Could not load agency admin users." })));
		}
	});
}

function approveAgencyAdmin(obj, f_id){
	$(obj).prop("disabled", true);
	$(obj).next("button").prop("disabled", true);
	$.ajax({
		type: "POST",
		url: "/agency/admins",
		data: {agency_admin_id: f_id, action: "approve"},
		success: function(data){
			$(obj).prop("disabled", false);
			$(obj).next("button").prop("disabled", false);
			if($(obj).closest("div.row").parent("div").children("div.row").length == 1){
				$(obj).closest("div.row").slideUp("slow", function (){
					$("#pending-admin").html(
					$("<h3>", { class: "text-center" }).html(
						$("<i>", { class: "fa fa-2x fa-times" })).add(
					$("<h4>", { class: "text-center", text: "No pending agency admin users." })));
				});
			}
			else{
				$(obj).closest("div.row").slideUp("slow", function (){
					$(obj).closest("div.row").next("hr").remove();
					$(obj).closest("div.row").remove();
				});
			}
		},
		error: function (){
			$(obj).prop("disabled", false);
			$(obj).next("button").prop("disabled", false);
		}
	});
}

function disapproveAgencyAdmin(obj, f_id){
	$(obj).prop("disabled", true);
	$(obj).prev("button").prop("disabled", true);
	$.ajax({
		type: "POST",
		url: "/agency/admins",
		data: {agency_admin_id: f_id, action: "disapprove"},
		success: function(data){
			$(obj).prop("disabled", false);
			$(obj).prev("button").prop("disabled", false);
			if($(obj).closest("div.row").parent("div").children("div.row").length == 1){
				$("#for-review").html(
					$("<h3>", { class: "text-center" }).html(
						$("<i>", { class: "fa fa-2x fa-times" })).add(
					$("<h4>", { class: "text-center", text: "No pending agency admin users." })));
			}
			else{
				$(obj).closest("div.row").next("hr").remove();
				$(obj).closest("div.row").remove();
			}
		},
		error: function (){
			$(obj).prev("button").prop("disabled", false);
			$(obj).prop("disabled", false);
		}
	});
}