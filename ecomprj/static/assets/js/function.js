console.log("working fine");


const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept",
    "Oct", "Nov", "Dec"];

$("#commentForm").submit(function (e) {
    e.preventDefault();

    let date = new Date();
    let time = date.getDay() + ' ' + monthNames[date.getUTCMonth()] + ' ' + date.getFullYear()

    $.ajax({
        data: $(this).serialize(),

        method: $(this).attr("method"),

        url: $(this).attr("action"),

        dataType: "json",

        success: function (res) {
            console.log("Comment Saved to Database");

            if(res.bool == true) {
                $('#review-res').html('Review Added')
                $('.hide-comment-form').hide()
                $('.add-review').hide()

                let _html = '<div class="single-comment justify-content-between d-flex mb-30">'
                _html += '<div class="user justify-content-between d-flex">'
                _html += '<div class="thumb text-center">'
                _html += '<img src="https://thumbs.dreamstime.com/b/default-avatar-profile-vector-user-profile-default-avatar-profile-vector-user-profile-profile-179376714.jpg" alt="" />'
                _html += '<a href="#" class="font-heading text-brand">' + res.context.user + '</a>'
                _html += '</div>'

                _html += '<div class="desc">'
                _html += '<div class="d-flex justify-content-between mb-10">'
                _html += '<div class="d-flex align-items-center">'
                _html += '<span class="font-xs text-muted">' + time + ' </span>'
                _html += '</div>'

                for (var i = 1; i <= res.context.rating; i++) {
                    _html += '<i class="fas fa-star text-warning"></i>';
                }


                _html += '</div>'
                _html += '<p class="mb-10">' + res.context.review + '</p>'

                _html += '</div>'
                _html += '</div>'
                _html += ' </div>'

                $(".comment-list").prepend(_html)


            }

        }
    })
})


$(document).ready(function () {
    $(".filter-checkbox, #price-filter-btn").on("click", function () {
        console.log("A checkbox was clicked");

        let filter_object = {}

        let min_price = $('#max_price').attr('min')
        let max_price = $('#max_price').val()

        filter_object.min_price = min_price;
        filter_object.max_price = max_price;

        $(".filter-checkbox").each(function () {
            let filter_value = $(this).val();
            let filter_key = $(this).data("filter"); //vendor, category

            // console.log("Filter value is:",filter_value );
            // console.log("Filter value is:",filter_key );

            filter_object[filter_key] = Array.from(document.querySelectorAll('input[data-filter=' + filter_key + ']:checked')).map(function (element) {
                return element.value;
            })
        })
        console.log("Filter object is: ", filter_object);
        $.ajax({
            url: '/filter-products',
            data: filter_object,
            dataType : 'json',
            beforeSend: function(){
                console.log('Trying to filter products...');
            },
            success: function(response){
                console.log(response);
                console.log('Data filtered successfully');
                $('#filtered-products').html(response.data);
            }
        })
    })

    $('#max_price').on('blur', function(){
        let min_price = $(this).attr('min')
        let max_price = $(this).attr('max')
        let current_price = $(this).val()

        // console.log('Current price is:', current_price);
        // console.log('Max price is:', max_price);
        // console.log('Min price is:', min_price);

        if(current_price < parseInt(min_price) || current_price > parseInt(max_price)){
            // console.log('Price is out of range');

            min_price = Math.round(min_price * 100) / 100
            max_price = Math.round(max_price * 100) / 100


            // console.log('Max price is:', max_Price);
            // console.log('Min price is:', min_Price);

            alert('Price should be between $' +min_price + ' and $' +max_price);
            $(this).val(min_price)
            $('#range').val(min_price)
            $(this).focus()

            return false

        }
    })
        // add a cart functionality
    $('.add-to-cart-btn').on('click', function(){

        let this_val = $(this)
        let index_val = this_val.attr('data-index')

        let quantity = $('.product-quantity-' + index_val).val()
        let product_title = $('.product-title-' + index_val).val()
        let product_id = $('.product-id-' + index_val).val()
        let product_price = $('.current-product-price-' + index_val).text()
        let product_pid = $('.product-pid-' + index_val).val()
        let product_image = $('.product-image-' + index_val).val()

        console.log('Quantity:', quantity);
        console.log('Title:', product_title);
        console.log('ID:', product_id);
        console.log('PID:', product_pid);
        console.log('Image:', product_image);
        console.log('Index:', index_val);
        console.log('Price:', product_price);
        console.log('Current Element:', this_val);

        $.ajax({
            url: '/add-to-cart',
            data: {
                'id': product_id,
                'pid': product_pid,
                'image': product_image,
                'quantity': quantity,
                'title': product_title,
                'price': product_price
            },
            dataType: 'json',
            beforeSend: function(){
                console.log('Adding to cart...');
            },
            success: function(response) {
                this_val.html('✔')
                console.log('Added to cart');
                $('.cart-items-count').text(response.totalcartitems)
            }
        })
    })

    $(document).on('click', '.delete-product', function(){

        let product_id = $(this).attr('data-product')
        let this_val = $(this)

        console.log('Product ID:', product_id);

        $.ajax({
            url: '/delete-from-cart',
            data: {
                'id': product_id
            },
            dataType: 'json',
            beforeSend: function(){
                this_val.hide()
            },
            success: function(response){
                this_val.show()
                $('.cart-items-count').text(response.totalcartitems)
                $('#cart-list').html(response.data)
            }
        })
    })

    $(".update-product").on("click", function () {

        let product_id = $(this).attr("data-product")
        let this_val = $(this)
        let product_quantity = $('.product-quantity-' + product_id).val()


        console.log('Product ID:', product_id);
        console.log('Product Qty:', product_quantity);

        $.ajax({
            url: '/update-cart',
            data: {
                'id': product_id,
                'quantity': product_quantity,
            },
            dataType: 'json',
            beforeSend: function(){
                this_val.hide()
            },
            success: function(response){
                this_val.show()
                $('.cart-items-count').text(response.totalcartitems)
                $('#cart-list').html(response.data)
                window.location.reload()
            }
        })
    })


    // Making Default addresses
    $(document).on('click', '.make-default-address', function () {
        let id = $(this).attr('data-address-id')
        let this_val = $(this)

        console.log('Address ID:', id);
        console.log('Element is:', this_val);

        $.ajax({
            url: '/make-default-address',
            data: {
                'id': id
            },
            dataType: 'json',
            success: function (response){
                console.log('Address made default');
                if (response.boolean == true) {

                    $(".check").hide()
                    $(".action_btn").show()

                    $(".check" + id).show()
                    $(".button" + id).hide()

                }

            }
        })
    })
    // Adding to wishlist
    $(document).on('click', '.add-to-wishlist', function() {
        let product_id = $(this).attr('data-product-item')
        let this_val = $(this)

        console.log('Product ID:', product_id);

        $.ajax({
            url: '/add-to-wishlist',
            data: {
                'id': product_id
            },
            dataType: 'json',
            beforeSend: function() {
                this_val.html('✔')
            },
            success: function(response) {
                if (response.bool === true) {
                    console.log('Added to wishlist');
                }
            }
        })
    })
    // Remove from wishlist
        $(document).on('click', '.delete-wishlist-product', function() {
        let wishlist_id = $(this).attr('data-wishlist-product')
        let this_val = $(this)

        console.log('Wishlist ID:', wishlist_id);

        $.ajax({
            url: '/delete-from-wishlist',
            data: {
                'id': wishlist_id
            },
            dataType: 'json',
            beforeSend: function(){
                console.log('Deleting product from wishlist...');
            },
                success: function(response){
                // Удалите элемент из DOM вместо замены всего HTML
                this_val.closest('tr').remove();

                // Обновите количество товаров в списке желаний
                $('.count-items').text(response.wishlist_count);
                var remainingText = ' product' + (response.wishlist_count != 1 ? 's' : '') + ' in this list';
                $('h6.text-body').contents().last()[0].textContent = remainingText;
            }
        })
    })
    // Grabbing info from the form
    $(document).on('submit', '#contact-form-ajax', function (e){
        e.preventDefault();
        console.log('Form submitted');

        let full_name = $('#full_name').val()
        let email = $('#email').val()
        let phone = $('#phone').val()
        let subject = $('#subject').val()
        let message = $('#message').val()

        console.log('Name:', full_name);
        console.log('Email:', email);
        console.log('Phone:', phone);
        console.log('Subject:', subject);
        console.log('Message:', message);

        $.ajax({
            url: '/ajax-contact-form',
            data: {
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'subject': subject,
                'message': message
            },
            dataType: 'json',
            beforeSend: function(){
                console.log('Sending data to server...');
            },
            success: function(res){
                console.log('Data sent successfully');
                $('.contact_us_p').hide()
                $('#contact-form-ajax').hide()
                $('#message-response').html('Message sent successfully')

            }
        })
    })
})


//    $('.add-to-cart-btn').on('click', function(){
//         let quantity = $('#product-quantity').val()
//         let product_title = $('.product-title').val()
//         let product_id = $('.product-id').val()
//         let product_price = $('#current-product-price').text()
//         let this_val = $(this)
//
//         console.log('Quantity:', quantity);
//         console.log('Title:', product_title);
//         console.log('Id:', product_id);
//         console.log('Price:', product_price);
//         console.log('Current Element:', this_val);
//
//         $.ajax({
//             url: '/add-to-cart',
//             data: {
//                 'id': product_id,
//                 'quantity': quantity,
//                 'title': product_title,
//                 'price': product_price
//             },
//             dataType: 'json',
//             beforeSend: function(){
//                 console.log('Adding to cart...');
//             },
//             success: function(response) {
//                 this_val.html('Item added to cart')
//                 console.log('Added to cart...');
//                 $('.cart-items-count').text(response.totalcartitems)
//             }
//         })
//     })
// })




