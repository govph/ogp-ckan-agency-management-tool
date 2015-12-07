$(document).ready(function(){
    $('input[name=new_password]').focus();
});
$("#registerAccountForm").submit(function (e){
    $("div.form-group").removeClass("has-error");
    $("p.help-block").remove();
    if($("#new_password").val().length < 8){
        $("#new_password").parent("div.form-group").addClass("has-error");
        $("#new_password").after($("<p>", { class: "help-block", text: "Password must be atleast 8 characters long." }))
        e.preventDefault();
        $("#new_password").focus();
        return
    }
    if($("#new_password").val() != $("#confirm_password").val()){
        $("#confirm_password").parent("div.form-group").addClass("has-error");
        $("#confirm_password").after($("<p>", { class: "help-block", text: "Passwords do not match." }))
        e.preventDefault();
        $("#confirm_password").focus();
        return
    }
    $(".btn-inverse").prop("disabled", true).html($("<i>", { class: "fa fa-spin fa-circle-o-notch" })).append(" SAVE PASSWORD");
    $(".form-control").prop("readonly", true);
});
$("#new_password").keyup(function (){
    if(this.value.length >= 8){
        $(this).parent("div.form-group").removeClass("has-error");
        $(this).next("p.help-block").remove();
    }
});
$("#confirm_password").keyup(function (){
    if(this.value == $("#new_password").val()){
        $(this).parent("div.form-group").removeClass("has-error");
        $(this).next("p.help-block").remove();
    }
});