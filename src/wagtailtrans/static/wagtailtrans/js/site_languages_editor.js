$(function(){
	$('#id_other_languages option[value="' + $('#id_default_language').val() + '"]')
			.attr('selected', false)
			.attr('disabled', true);
	$('#id_default_language').change(function(evt){
		$('#id_other_languages option').attr('disabled', false);
		$('#id_other_languages option[value="' + evt.target.value + '"]')
			.attr('selected', false)
			.attr('disabled', true);
	});
});
