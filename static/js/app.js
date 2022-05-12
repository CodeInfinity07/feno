function loading() {
    $('.container').hide();
    $('.loading_img').show();
}

function loaded() {
    $('.container').show();
    $('.loading_img').hide();
}


$(document).ready(function () {

    $("form").submit(function (evt) {
        evt.preventDefault();
        loading();
        var formData = new FormData($(this)[0]);

        $.ajax({
            url: '/analyse',
            type: 'POST',
            data: formData,
            // async: false,
            // cache: false,
            contentType: false,
            enctype: 'multipart/form-data',
            processData: false,
            success: function (response) {

                $('html').html(response);
                loaded();

            },
            error: function (response) {
                console.log(response);
            },


        });

        return false;

    });
});

