var settings = {
	'serverUrl' : '/'
};
var allSculptureData = false;
/*var templateData = {
	'sculptureControl' : {
		'tag' : 'div',
		'contents' : [
			'*/


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
		buildElement('sculptureControl', 'mainDiv', {'sculptureId' : data['activeSculptureId']});
		$('#sculptureControl').tabs();
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
				'<select id="sculptureChooser" onChange="changeSculpture()" size="10"><option value="none">None</option></select>'
			);
			$.each(allSculptureData['sculptures'], function(sculptureId, sculptureData) {
				$('#sculptureChooser').append(makeHtml({
					'tag' : 'option',
					'id' : sculptureId + '_choice',
					'value' : sculptureId
				}));
				$('#' + sculptureId + '_choice').append(allSculptureData.sculptures[sculptureId].config.sculptureName);
			});
			$('#sculptureChooser').menu();
		break;
		case 'sculptureControl':
			$(htmlParentId).append(
				'<h1>' + allSculptureData.sculptures[dataPath.sculptureId].config.sculptureName + '</h1><div id="sculptureControl"><ul id="sculptureControlTabLabels"></ul></div>'
			);
			$.each( allSculptureData.sculptures[dataPath.sculptureId].modules, function( moduleId, moduleData ) {
				$('#sculptureControl').append(
					'<div id="' + moduleId + '_module"></div>'
				);
				$('#sculptureControlTabLabels').append(
					'<li><a href="#' + moduleId + '_module">' + allSculptureData.sculptures[dataPath.sculptureId].config.modules[moduleId].name + '</a></li>'
				);
				
				buildElement('module', moduleId + '_module', {'sculptureId' : dataPath.sculptureId, 'moduleId' : moduleId});
			});
		break;
		case 'module':
			$(htmlParentId).append(makeHtml({
				'tag' : 'select',
				'id' : dataPath.moduleId + '_patternChoices',
				'onChange' : "addPattern('" + dataPath.moduleId + "')",
				'class' : 'addPattern'
			}));
			$('#' + dataPath.moduleId + '_patternChoices').append('<option value="none">Add Pattern</option>');
			$.each( allSculptureData.sculptures[dataPath.sculptureId].modules[dataPath.moduleId].availablePatternNames, function( patternId, patternData ) {
				$('#' + dataPath.moduleId + '_patternChoices').append('<option value="' + patternData + '">' + patternData + '</option>');
			});
			$('#' + dataPath.moduleId + '_patternChoices').menu();

			$(htmlParentId).append(
				'<div id="' + dataPath.moduleId  + '_outputView" class="outputView"></div><div id="' + dataPath.moduleId  + '_patternView" class="patternView"></div><div id="' + dataPath.moduleId  + '_inputView" class="inputView"></div>'
			);
			buildElement('outputView', dataPath.moduleId  + '_outputView', dataPath);
			buildElement('patternView', dataPath.moduleId  + '_patternView', dataPath);
			buildElement('inputView', dataPath.moduleId  + '_inputView', dataPath);
			
		break;
		case 'patternView':
			$(htmlParentId).append(makeHtml({
				'tag' : 'select',
				'id' : dataPath.moduleId + '_patternSelection',
				'onChange' : "editPattern('" + dataPath.moduleId + "')",
				'class' : 'activePatternList',
				'size' : '10'
			}));
			$.each( allSculptureData.sculptures[dataPath.sculptureId].modules[dataPath.moduleId].patterns, function( patternId, patternData ) {
				$('#' + dataPath.moduleId + '_patternSelection').append('<option value="' + patternId + '">' + patternData['name'] + '</option>');
			});
			$('#' + dataPath.moduleId + '_patternSelection').menu();

		break;
		case 'inputView':
			$.each( allSculptureData.sculptures[dataPath.sculptureId].modules[dataPath.moduleId].inputs, function( inputInstanceId, inputData ) {
				divId  = dataPath.moduleId + '_inputInstance' + inputInstanceId + '_div';
				$(htmlParentId).append(
					'<div id="' + divId + '"></div>'
				);
				buildElement('input', divId, {'sculptureId' : dataPath.sculptureId, 'moduleId' : dataPath.moduleId, 'inputInstanceId' : inputInstanceId});
			});
		break;
		case 'outputView':
			$.each( allSculptureData.sculptures[dataPath.sculptureId].config.modules[dataPath.moduleId].protocol.mapping, function( rowIndex, col ) {
				$(htmlParentId).append(
					'<div id="' + dataPath.moduleId + '_outputView_row' + rowIndex + '"></div>'
				);
				$.each(allSculptureData.sculptures[dataPath.sculptureId].config.modules[dataPath.moduleId].protocol.mapping[rowIndex], function( colIndex, foo ) {
					$('#' + dataPath.moduleId + '_outputView_row' + rowIndex).append(
						'<input type="checkbox" id="' + dataPath.moduleId + '_outputView_row' + rowIndex + '_col' + colIndex + '">'
					);
				});
			});
		break;
		case 'input':
			inputData = allSculptureData.sculptures[dataPath.sculptureId].modules[dataPath.moduleId].inputs[dataPath.inputInstanceId];
			if (inputData['settings']){
				$.each( inputData['settings'], function( settingIndex, settingData ) {
					tagData={};
					makeKnob = false;
					switch(settingData['type']){
						case 'onOff':
							tagData = {
								'tag' : 'input',
								'type' : 'checkbox',
								'selfClosing' : true
							};
						break;
						case 'param':
							tagData = {
								'tag' : 'input',
								'value' : settingData['currentSetting'],
								'selfClosing' : true,
								'data-width' : 100,
								'data-max' : settingData.max,
								'data-min' : settingData.min,
								'data-skin' : 'tron',
								'class' : 'knob',
								'data-thickness' : '.2' 
							};
							makeKnob = true;
						break;
					}
					tagData['id'] = dataPath.moduleId + '_input' + dataPath.inputInstanceId + '_setting' + settingIndex
					tagData['onChange'] = "setInputValue('" + dataPath.moduleId + "', " + dataPath.inputInstanceId + ", " + settingIndex + ")"
					$(htmlParentId).append(makeHtml(tagData));
					if (makeKnob){
						initKnob(tagData['id'], dataPath.moduleId, dataPath.inputInstanceId, settingIndex);
					
					}

				});
			}

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
function addPattern(moduleId){
	inputId = '#' + moduleId + '_patternChoices';
	if ($(inputId).val() != 'none'){
		doCommand(['addPattern', moduleId, $(inputId).val()]);
		$(inputId).val('none');
	}
}
function setInputValue(moduleId, inputInstanceId, settingIndex){
	htmlId = "#" + moduleId + '_input' + inputInstanceId + '_setting' + settingIndex;
	doCommand(['setInputValue', moduleId, parseInt(inputInstanceId), $(htmlId).val(), parseInt(settingIndex)]);
	
}
function initKnob(htmlId, moduleId, inputInstanceId, settingIndex){
	htmlId = '#' + htmlId;
	$(htmlId).knob({
		release : function (value) {
			setInputValue(moduleId, inputInstanceId, settingIndex);
		},
		draw : function () {

				// "tron" case
				if(this.$.data('skin') == 'tron') {

						this.cursorExt = 0.3;

						var a = this.arc(this.cv)  // Arc
								, pa                   // Previous arc
								, r = 1;

						this.g.lineWidth = this.lineWidth;

						if (this.o.displayPrevious) {
								pa = this.arc(this.v);
								this.g.beginPath();
								this.g.strokeStyle = this.pColor;
								this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, pa.s, pa.e, pa.d);
								this.g.stroke();
						}

						this.g.beginPath();
						this.g.strokeStyle = r ? this.o.fgColor : this.fgColor ;
						this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, a.s, a.e, a.d);
						this.g.stroke();

						this.g.lineWidth = 2;
						this.g.beginPath();
						this.g.strokeStyle = this.o.fgColor;
						this.g.arc( this.xy, this.xy, this.radius - this.lineWidth + 1 + this.lineWidth * 2 / 3, 0, 2 * Math.PI, false);
						this.g.stroke();

						return false;
				}
		}	
	});
}
