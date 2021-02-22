$("#coupon-generator").on('click', function () {
      $.ajax({
        url: '/admin/settings',
        dataType: 'json',
        success: function (data) {
          if (data.status == "success") {
            alert('Coupon created!')
          } else {
            alert('Something went wrong with creating the coupon.')
          }
        }
      });
    });

$(".field-generate_stripe_product span").on('click', function () {
      var id = $(this).attr('data-id')
      $.ajax({
        url: '/generate_stripe_product/' + id,
        dataType: 'json',
        success: function (data) {
          if (data.status == "success") {
            alert('Product is generated in Stripe')
          } else {
            alert('Product with price id is already in Stripe')
          }
        }
      });
    });