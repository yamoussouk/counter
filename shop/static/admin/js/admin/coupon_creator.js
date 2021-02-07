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