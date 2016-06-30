(function ($) {
	$(document).ready(function(){
		$("#loginModal input[name='hasaccount'][value='1']").click();
		$("#loginModal input[name='hasaccount']").change(function() {
			switch ($("#loginModal input[name='hasaccount']:checked").val()) {
				case '0':
					$('#loginModal #loginform').hide();
					$('#loginModal #registerform').show();
					break;
				default:
					$('#loginModal #loginform').show();
					$('#loginModal #registerform').hide();
					break;
			}
		});
	});
})(jQuery);