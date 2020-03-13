$(document).ready(function() {

// Show modal and disable button

    $("#btnSubmit").click(function () {
        setTimeout(function () { disableButton(); }, 0);
    });

    function disableButton() {
        $("#btnSubmit").prop('disabled', true);
        setTimeout(function() {
                $('#modalPush').modal('show');
                }, 1000);
      };

});