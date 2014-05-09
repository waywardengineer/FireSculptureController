settings = {
	'serverUrl' : '/'
};
allSculptureData = false


function doInit(){
	$.ajax(settings.serverUrl + 'getData', {
		dataType: 'json'
	}).done(function(result) {
		buildAll(result);
	});
}
function buildAll(data){
	allSculptureData = data
	$('#mainDiv').html('');
	if (data['activeSculptureId']){
		buildElement('sculptureControl', 'mainDiv', [data['activeSculptureId']]);
	}
	else {
		buildElement('sculptureChooser', 'mainDiv');
	}
}
function buildElement(elementType, htmlParentId, dataPath){
	htmlParentId = '#' + htmlParentId
	switch(elementType){
		case 'sculptureChooser':
			$(htmlParentId).append(
				'<select id="sculptureChooser" onChange="changeSculpture()"><option value="none">None</option></select>'
			);
			$.each(allSculptureData['sculptures'], function(sculptureId, sculptureData) {
				$('#sculptureChooser').append(makeHtml({
					'tag' : 'option',
					'id' : sculptureId + '_choice',
					'value' : sculptureId
				}));
				$('#' + sculptureId + '_choice').append(allSculptureData.sculptures[sculptureId].config.sculptureName);
			});
		break;
		case 'sculptureControl':
			$(htmlParentId).append(
				'<div id="sculptureControl"><ul id="sculptureControlTabLabels"></ul></div>'
			);
			$.each( allSculptureData.sculptures[dataPath[0]].modules, function( moduleId, moduleData ) {
				$('#sculptureControl').append(
					'<div id="' + moduleId + '_module"></div>'
				);
				$('#sculptureControlTabLabels').append(
					'<li><a href="#' + moduleId + '_module">' + allSculptureData.sculptures[dataPath[0]].config.modules[moduleId].name + '</a></li>'
				);
				buildElement('module', moduleId + '_module', [dataPath[0], moduleId]);
			});
		break;
	}
}
function makeHtml(tagData){
	result = '<' + tagData['tag'];
	$.each(tagData, function(k, v){
		if ($.inArray(k, ['tag', 'selfClosing']) < 0){
			result += ' ' + k + ' = "' + v + '"';
		}
	});
	result += '>';
	if (!tagData['selfClosing']){
		result += '</' + tagData['tag'] + '>';
	}
	return result;
}
function changeSculpture(){
	if ($('#sculptureChooser').val() != 'none'){
		doCommand(['loadSculpture', $('#sculptureChooser').val()]);
	}
}
function doCommand(command){
	$.ajax(settings.serverUrl + 'doCommand', {
		data : JSON.stringify(command),
		contentType : 'application/json',
		type : 'POST',
		dataType: 'json',
	}).done(function(result) {
		handleCommandResult(result);
	});
}
function handleCommandResult(result){
	switch(result.command){
		case 'loadSculpture':
			doInit();
		break;
	}
}


