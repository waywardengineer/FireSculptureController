var settings = {
	'serverUrl' : '/'
};
var allSculptureData = false;
var source = new EventSource('/dataStream');
source.onmessage = function (event) {
	var data = JSON.parse(event.data);
	if (data.log){
		$.each(data.log, function(logIndex, logItem){
			$('#logDiv').prepend(logItem + '<br>');
		});
	}
	if (data.sculptures){
		allSculptureData.sculptures = $.extend(true, allSculptureData.sculptures, data.sculptures);
		updateStatusDisplay();
	}
	if (data.outputChanges){
		$.each(data.outputChanges, function(index, outputChangeMessage){
			$.each(outputChangeMessage.data, function(index, pointData){
				id = outputChangeMessage.moduleId + '_outputView_row' + pointData[0][0] + '_col' + pointData[0][1];
				$('#' + id).prop('checked', pointData[1][0]).button('refresh');
			});
		});
	}
};



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
	if (data.currentSculpture){
		$('#mainDiv').append($('#sculptureControllerTemplate').render(makeSculptureControllerTemplateData()));
		$.each( allSculptureData.inputs, function( inputInstanceId, inputData ) {
			buildInputControls(inputInstanceId, inputData);
		});
		$.each( allSculptureData.currentSculpture.modules, function( moduleId, moduleData ) {
			$('#' + moduleId + '_patternChoices').menu();
			$('#' + moduleId + '_patternSelection').menu();
		});
		$('.pooferDisplay').button();
		$('#sculptureControl').tabs();
	}
	else {
		data = {"sculptures" : []};
		$.each(allSculptureData['sculptures'], function(sculptureId, sculptureData) {
			data.sculptures.push({"sculptureId" : sculptureId, "sculptureName" : sculptureData.config.sculptureName});
		});
		$('#mainDiv').append($('#sculptureChooserTemplate').render(data));
		$('#sculptureChooser').menu();
	}
	$('#mainDiv').css('height', $(window).height() * 0.7 + 'px');
	$('#logDiv').css('height', $(window).height() * 0.25 + 'px');
}

function makeSculptureControllerTemplateData(){
	data = {"sculptureName" : allSculptureData.currentSculpture.sculptureId, "modules" : [], "inputs" : []};
	$.each( allSculptureData.inputs, function( inputInstanceId, inputdata ) {
		data.inputs.push({"inputInstanceId" : inputInstanceId});
	});
	$.each( allSculptureData.currentSculpture.modules, function( moduleId, moduleData ) {
		templateModuleData = {"moduleId" : moduleId, "name" : moduleData.name, "availablePatternNames" : [], "patterns" : [], "inputs" : [], "rows" : []};
		$.each( moduleData.availablePatternNames, function( patternIndex, patternName ) {
			templateModuleData.availablePatternNames.push({"name" : patternName});
		});
		$.each( moduleData.patterns, function( patternInstanceId, patternData ) {
			templateModuleData.patterns.push({"patternName" : patternData.name, "patternInstanceId" : patternInstanceId});
		});
		$.each( moduleData.protocol.mapping, function( rowIndex, rowData ) {
			templateRowData = {"rowIndex" : rowIndex, "moduleId" : moduleId, "cols" : []};
			$.each( rowData, function( colIndex, colData ) {
				templateRowData.cols.push({"rowIndex" : rowIndex, "moduleId" : moduleId, "colIndex" : colIndex});
			});
			templateModuleData.rows.push(templateRowData);
		});
		data.modules.push(templateModuleData);
	});
	return data;
}

function buildInputControls(inputInstanceId, inputData){
	htmlParentId = "#inputInstance" + inputInstanceId + "_div"
	if (inputData.inputs){
		$.each( inputData.inputs, function( settingIndex, settingData ) {
			tagData={};
			makeKnob = false;
			switch(settingData['type']){
				case 'pulse':
					tagData = {
						'tag' : 'input',
						'type' : 'checkbox',
						'selfClosing' : true
					};
				break;
				case 'value':
					tagData = {
						'tag' : 'input',
						'value' : settingData.currentValue,
						'selfClosing' : true,
						'data-width' : 100,
						'data-height' : 100,
						'data-max' : settingData.max,
						'data-min' : settingData.min,
						'data-skin' : 'tron',
						'class' : 'knob',
						'data-thickness' : '.2' 
					};
					makeKnob = true;
				break;
			}
			tagData['id'] = 'inputInstance' + inputInstanceId + '_setting' + settingIndex;
			tagData['onChange'] = "setInputValue(" + inputInstanceId + ", " + settingIndex + ")";
			$(htmlParentId).append('<div class="controlContainer">' + makeHtml(tagData) + '</div>');
			$(htmlParentId).append('<span class="settingLabel">' + settingData.name + '</span>');
			if (makeKnob){
				initKnob(tagData['id'], inputInstanceId, settingIndex);
			}
		});
	}
}
function editPattern(moduleId){
	patternInstanceId = $('#' + moduleId + '_patternSelection').val();
	$.each(allSculptureData.sculptures[allSculptureData.activeSculptureId].modules[moduleId].inputs, function(inputInstanceId){
		$('#' + moduleId + '_inputInstance' + inputInstanceId + '_div').css("display", "none");
	});
	$.each(allSculptureData.sculptures[allSculptureData.activeSculptureId].modules[moduleId].patterns[patternInstanceId].inputBindings, function(patternInputId, patternInputData){
		idPrefix  = moduleId + '_inputInstance' + patternInputData.inputInstanceId + '_';
		$('#' + idPrefix + 'div').css("display", "block");
		$('#' + idPrefix + 'description').html(patternInputData.description);
	});

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
		case 'addPattern':
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
function updateStatusDisplay(){
	if (allSculptureData.activeSculptureId){
		$.each(allSculptureData.sculptures[allSculptureData.activeSculptureId].modules, function(moduleId, moduleData){
			$.each(moduleData.currentOutputState, function(rowIndex, rowData){
				$.each(rowData, function(colIndex, colData){
					id =  moduleId + '_outputView_row' + rowIndex + '_col' + colIndex;
					$('#' + id).prop('checked', colData).button('refresh');
				});
			});
		});
	}
	
}

function initKnob(htmlId, inputInstanceId, settingIndex){
	htmlId = '#' + htmlId;
	$(htmlId).knob({
		release : function (value) {
			setInputValue(inputInstanceId, settingIndex);
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
