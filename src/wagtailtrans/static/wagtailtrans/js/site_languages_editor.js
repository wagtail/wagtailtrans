$(function(){
	var cb = $(':checkbox[name="other_languages"][value=' + $('#id_default_language').val() + ']');
	cb.attr('checked', false).attr('disabled', true);
	$('label[for="' + cb.attr('id') +'"]').css({'opacity': 0.6});
	$('#id_default_language').change(function(evt){
		$(':checkbox[name="other_languages"]').attr('disabled', false);
		$('label').css({'opacity': 1})
		cb = $(':checkbox[name="other_languages"][value=' + evt.target.value + ']');
		cb.attr('checked', false).attr('disabled', true);
		$('label[for="' + cb.attr('id') +'"]').css({'opacity': 0.6});
	});
});
