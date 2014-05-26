var settings = {
	'serverUrl' : '/'
};
var allSculptureData = false;
var currentView = {'activeTab' : false, 'activeModule' : false, activeSections : {}, sculptureIsLoaded:false}
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
	if (data.outputChanged){
		$.each(data.outputChanged, function(index, outputChangeMessage){
			$.each(outputChangeMessage.data, function(index, pointData){
				id = outputChangeMessage.moduleId + '_outputView_row' + pointData[0][0] + '_col' + pointData[0][1];
				$('#' + id).prop('checked', pointData[1][0]).button('refresh');
			});
		});
	}
};

function typesAreCompatible(type1, type2){
	result = false;
	if ((type1 == type2) || (type1 == 'pulse' && type2 == 'toggle') ||  (type2 == 'pulse' && type1 == 'toggle')){
		result = true;
	}
	return result;

}

function showRebindDialog(moduleId, patternInstanceId, patternInputId){
	selectData = {'id' : 'inputSelector', 'onChange' : 'onChange = "showInputParamsForm()"', 'options' : [{'description' : 'Select Input', 'value' : 'none'}]};
	inputChannelType = allSculptureData.currentSculpture.modules[moduleId].patterns[patternInstanceId].inputs[patternInputId].type;
	$.each(allSculptureData.availableInputTypes[inputChannelType], function(subType, typeData){
		selectData.options.push({'description' : "(New)" + typeData.longDescription, 'value' : JSON.stringify(['new', inputChannelType, subType])});
	});
	if (inputChannelType != 'multi'){
		$.each(allSculptureData.inputs, function(inputInstanceId, inputData){
			if ($.inArray(parseInt(inputInstanceId), allSculptureData.globalInputs) > -1){
				$.each(inputData.outputs, function(outputIndex, outputData){
					$('#logDiv').prepend(outputIndex + '<br>');
					if (typesAreCompatible(outputData.type, inputChannelType) ){
						selectData.options.push({'description' : "(Running)" + inputData.shortDescription + ' ' + outputData.description, 'value' : JSON.stringify(['running', inputInstanceId , outputIndex])});
					}
				});
			}
		});
	}
	$('#dialog').append($('#selectTemplate').render(selectData));
	$('#dialog').append('<div id="dialogInputs"></div>');
	$('#dialog').dialog({
		autoOpen: true,
		height: 300,
		width: 350,
		modal: true,
		buttons: {
			"Update": function() {
				doNewInputBinding(moduleId, patternInstanceId, patternInputId);
				$(this).dialog("close");
			},
			"Cancel": function() {
				$(this).dialog("close");
			}
		},
		close: function(event, ui) {
			$(this).empty().dialog('destroy');
		}
	});
}
function showGlobalInputDialog(){
	selectData = {'id' : 'inputSelector', 'onChange' : 'onChange = "showInputParamsForm()"', 'options' : [{'description' : 'Select Input', 'value' : 'none'}]};
	$.each(allSculptureData.availableGlobalInputs, function(typeIndex, typeData){
		selectData.options.push({'description' : allSculptureData.availableInputTypes[typeData[0]][typeData[1]].longDescription, 'value' : JSON.stringify(['new', typeData[0], typeData[1]])});
	});
	$('#dialog').append($('#selectTemplate').render(selectData));
	$('#dialog').append('<div id="dialogInputs"></div>');
	$('#dialog').dialog({
		autoOpen: true,
		height: 300,
		width: 350,
		modal: true,
		buttons: {
			"Update": function() {
				doNewInputBinding('main');
				$(this).dialog("close");
			},
			"Cancel": function() {
				$(this).dialog("close");
			}
		},
		close: function(event, ui) {
			$(this).empty().dialog('destroy');
		}
	});
}

function doNewInputBinding(moduleId, patternInstanceId, patternInputId){
	values = JSON.parse($('#inputSelector').val());
	if (values[0] == 'running'){
		doCommand(['changePatternInputBinding', moduleId, patternInstanceId, patternInputId, parseInt(values[1]), parseInt(values[2])])
	}
	else if (values[0] == 'new'){
		params = {'type' : values[1], 'subType' : values[2], 'inputs' : []}
		inputTypeData = allSculptureData.availableInputTypes[values[1]][values[2]];
		if (inputTypeData.initInputData){
			$.each(inputTypeData.initInputData, function (paramIndex, paramData){
				formInputId = '#inputDefinitionMainParam' + paramData[2];
				switch (paramData[0]){
					case 'text':
						params[paramData[2]] = $(formInputId).val();
					break;
					case 'int':
						params[paramData[2]] = parseInt($(formInputId).val());
					break;
					case 'bool':
						params[paramData[2]] = $(formInputId).is(":checked");
					break;
				}
			});
		}
		$.each(inputTypeData.inputs, function (inputIndex, inputData){
			configData = {}
			if (inputData.initInputData){
				paramsData = inputData.initInputData;
			}
			else if (inputData.type == 'value'){
				paramsData = [['int', 'Minimum', 'min'], ['int', 'Maximum', 'max']]
			}
			else {
				paramsData = []
			}
			$.each(paramsData, function (paramIndex, paramData){
				formInputId = '#inputDefinitionInputParam' + inputIndex + paramData[2];
				data = false;
				switch (paramData[0]){
					case 'text':
						data = $(formInputId).val();
					break;
					case 'int':
						data = parseInt($(formInputId).val());
					break;
					case 'bool':
						data = $(formInputId).is(":checked");
					break;
				}
				configData[paramData[2]] = data;
			});
			params.inputs.push(configData)
		});
		params = $.extend(true, inputTypeData, params);
		delete params.initInputData;
		if (moduleId == 'main'){
			doCommand(['addGlobalInput', params]);
		}
		else {
			doCommand(['bindPatternToNewInput', moduleId, patternInstanceId, patternInputId, params]);
		}
	}
}

function showInputParamsForm(){
	values = JSON.parse($('#inputSelector').val());
	formFields = [];
	if (values[0] == 'new'){
		inputTypeData = allSculptureData.availableInputTypes[values[1]][values[2]];
		if (inputTypeData.initInputData){
			$.each(inputTypeData.initInputData, function (paramIndex, paramData){
				fieldData = {"id" : "inputDefinitionMainParam" + paramData[2], "label" : paramData[1]}
				if (paramData[0] == 'text' || paramData[0] == 'int'){
					fieldData['input'] = true;
					if (inputTypeData[paramData[2]] != undefined){
						fieldData['value'] = inputTypeData[paramData[2]];
					}
				}
				else if (paramData[0] == 'bool'){
					fieldData['checkbox'] = true;
				}
				formFields.push(fieldData);
			});
		}
		$.each(inputTypeData.inputs, function (inputIndex, inputData){
			if (inputData.initInputData){
				paramsData = inputData.initInputData;
			}
			else if (inputData.type == 'value'){
				paramsData = [['int', 'Minimum', 'min'], ['int', 'Maximum', 'max']]
			}
			else {
				paramsData = []
			}
			$.each(paramsData, function (paramIndex, paramData){
				fieldData = {"id" : "inputDefinitionInputParam" + inputIndex + paramData[2], "label" : inputData.description + ':' + paramData[1]}
				if (paramData[2] in inputData){
					paramDefault = inputData[paramData[2]];
					if (typeof(paramDefault) == 'number'){
						fieldData['value'] = paramDefault.toString();
					}
					else if (typeof(paramDefault) == 'boolean'){
						if (paramDefault){
							fieldData['value'] = true;
						}
					}
					else {
						fieldData['value'] = paramDefault;
					}
				}
				if (paramData[0] == 'text' || paramData[0] == 'int'){
					fieldData['input'] = true;
				}
				else if (paramData[0] == 'bool'){
					fieldData['checkbox'] = true;
				}
				formFields.push(fieldData);
			});
		});
	}
	$('#dialogInputs').html($('#formFieldsTemplate').render({'fields' : formFields}));
}



function doInit(){
	reloadData();
}

function setCurrentModuleView(moduleId){
	currentView.activeModule = moduleId;
	if (currentView.activeSections[moduleId]){
		$('#' + currentView.activeSections[moduleId] + '_heading').click();
	}
}

function reloadData(){
	$.ajax(settings.serverUrl + 'getData', {
		dataType: 'json'
	}).done(function(result) {
		allSculptureData = result
		buildAll();
	});
}

function buildAll(){
	if (allSculptureData.currentSculpture){
		if (currentView.sculptureIsLoaded){
			$('#logStorage').html($('#logDiv').html());
		}
		$('#mainDiv').html('');
		$('#mainDiv').append($('#sculptureControllerTemplate').render(makeSculptureControllerTemplateData()));
		if (currentView.sculptureIsLoaded){
			$('#logDiv').html($('#logStorage').html());
		}
		$('#inputs').detach().appendTo('#storageDiv');
		$.each( allSculptureData.inputs, function( inputInstanceId, inputData ) {
			buildInputControls(inputInstanceId, inputData);
		});
		$( ".accordion" ).accordion({
			collabsible : true,
			active : 'none'
		});
		$.each( allSculptureData.currentSculpture.modules, function( moduleId, moduleData ) {
			$('#' + moduleId + '_patternChoices').menu();
			$('#' + moduleId + '_removePatternButton').button().click(function(e){
				patternId = $('#' + moduleId + '_patternSelection').val();
				if (patternId && patternId != 'none'){
					doCommand(['removePattern', moduleId, patternId]);
				}
			});
			$.each( moduleData.protocol.mapping, function( rowIndex, rowData ) {
				$.each( rowData, function( colIndex, colData ) {
					$('#' + moduleId + '_enableView_row' + rowIndex + '_col' + colIndex).button().click(function(e){
						doCommand(['toggleEnable', moduleId, [rowIndex, colIndex]]);
					});
				});
			});
		});
		$('.pooferDisplay').button();
		if (currentView.activeModule){
			$('#sculptureControl').tabs({ active : $("#sculptureControl>div").index($("#" + currentView.activeModule + '_module')) });
		}
		else{
			$('#sculptureControl').tabs();
		}
		$('#addGlobalInputButton').button().click(function(e){
			showGlobalInputDialog()
		});
		$('.globalInputButton').button({icons : {primary:"ui-icon-notice"}}).click(function(){
			doCommand(['removeGlobalInput', parseInt(this.id.split('_')[1])]);
		});
		$('.toggleRowButton').button().click(function(){
			parts = this.id.split('_');
			doCommand(['toggleRowSelection', parts[0], parts[1], parseInt(parts[2])]);
		});
		$('.removePatternButton').button({icons : {primary:"ui-icon-notice"}}).click(function(){
			parts = this.id.split('_');
			doCommand(['removePattern', parts[0], parts[1]]);
		});
		$('#safeButtonDiv').buttonset();
		$('#safeModeOn').click(function(e){
			doCommand(['setSafeMode', true]);
		});
		$('#safeModeOff').click(function(e){
			doCommand(['setSafeMode', false]);
		});
		if (currentView.activeModule){
			setCurrentModuleView(currentView.activeModule);
		}
	}
	else {
		data = {"sculptures" : []};
		$.each(allSculptureData['sculptures'], function(sculptureId, sculptureData) {
			data.sculptures.push({"sculptureId" : sculptureId, "sculptureName" : sculptureData.sculptureName});
		});
		$('#mainDiv').append($('#sculptureChooserTemplate').render(data));
		$('#sculptureChooser').menu();
	}
	$('#mainDiv').css('height', $(window).height() * 0.9 + 'px');
}


function makeSculptureControllerTemplateData(){
	data = {"sculptureName" : allSculptureData.currentSculpture.sculptureName, "modules" : [], "inputs" : []};
	$.each( allSculptureData.inputs, function( inputInstanceId, inputData ) {
		templateInputData = {"inputInstanceId" : inputInstanceId, "inputs" : []}
		$.each(inputData.inputs, function(inputIndex){
			templateInputData.inputs.push({'inputIndex' : inputIndex, 'inputInstanceId' : inputInstanceId});
		});
		data.inputs.push(templateInputData);
	});
	$.each( allSculptureData.currentSculpture.modules, function( moduleId, moduleData ) {
		templateModuleData = {"moduleId" : moduleId, "name" : moduleData.name, "availablePatternNames" : [], "patterns" : [], "inputs" : [], "rows" : []};
		$.each( moduleData.availablePatternNames, function( patternIndex, patternName ) {
			templateModuleData.availablePatternNames.push({"name" : patternName});
		});
		$.each( moduleData.patterns, function( patternInstanceId, patternData ) {
			templatePatternData = {"patternName" : patternData.name, "patternInstanceId" : patternInstanceId, "rowSettings" : [], "moduleId" : moduleId};
			$.each(patternData.rowSettings, function(rowIndex, rowSetting){
				rowData = {"moduleId" : moduleId, "patternInstanceId" : patternInstanceId, "rowIndex" : rowIndex};
				if (rowSetting) rowData['enabled'] = true;
				templatePatternData.rowSettings.push(rowData);
			});
			templateModuleData.patterns.push(templatePatternData);
		});
		$.each( moduleData.protocol.mapping, function( rowIndex, rowData ) {
			templateRowData = {"rowIndex" : rowIndex, "moduleId" : moduleId, "cols" : []};
			$.each( rowData, function( colIndex, colData ) {
				templateRowData.cols.push({"rowIndex" : rowIndex, "moduleId" : moduleId, "colIndex" : colIndex});
				if (moduleData.enabledStatus[rowIndex][colIndex]){
					templateRowData.cols[colIndex]['enabled'] = true;
				}
			});
			templateModuleData.rows.push(templateRowData);
		});
		data.modules.push(templateModuleData);
	});
	data['globalInputs'] = []
	$.each(allSculptureData.globalInputs, function (index, inputInstanceId){
		data.globalInputs.push({'value' : inputInstanceId.toString(), 'name' : allSculptureData.inputs[inputInstanceId].shortDescription})
	});
	if (allSculptureData.safeMode){
		data['safeMode'] = true;
	}
	return data;
}

function buildInputControls(inputInstanceId, inputData){
	if (inputData.inputs){
		$.each( inputData.inputs, function( settingIndex, settingData ) {
			tagData={};
			makeKnob = false;
			inputId = 'inputInstance' + inputInstanceId + '_input' + settingIndex;
			templateData = $.extend(true, {}, settingData);
			templateData['id'] = inputId;
			templateData['inputInstanceId'] = inputInstanceId;
			templateData['settingIndex'] = settingIndex;
			
			switch(settingData['type']){
				case 'pulse':
					$('#' + inputId + '_container').append($('#buttonTemplate').render(templateData));
					$('#' + inputId).button().click(function(e){
						doCommand(['setInputValue', parseInt(inputInstanceId), true]);
					});
				break;
				case 'toggle':
					if (settingData.currentValue){
						templateData['checked'] = 'checked="checked"';
					}
					else {
						templateData['checked'] = '';
					}
					$('#' + inputId + '_container').append($('#checkButtonTemplate').render(templateData));
					$('#' + inputId).button().click(function(e){
						setInputToggle(inputInstanceId, settingIndex);
					});
				break;
				case 'value':
					$('#' + inputId + '_container').append($('#knobTemplate').render(templateData));
					initKnob(inputId, inputInstanceId, settingIndex);
				break;
			}
			$('#' + inputId + '_description').html(settingData.description);
		});
	}
}

function showGlobalInput(inputInstanceId){
	hideAllInputs();
	inputData = allSculptureData.inputs[inputInstanceId];
	currentView.activeSections['main'] = inputInstanceId
	$('#inputs').detach().appendTo('#globalInput_' + inputInstanceId);
	$('#inputInstance' + inputInstanceId + '_div').css("display", "block");
	$('#inputInstance' + inputInstanceId + '_description').html(inputData.shortDescription);
	$('#inputInstance' + inputInstanceId + '_outputs').html('<ul>');
	$.each(inputData.outputs, function(outputIndex, outputData){
		$('#inputInstance' + inputInstanceId + '_outputs').append('<li class="descriptionText">' + outputData.description + '</li>');
	});
	$('#inputInstance' + inputInstanceId + '_outputs').append('</ul>');
}

function hideAllInputs(){

	$.each(allSculptureData.inputs, function(inputInstanceId, inputData){
		$('#inputInstance' + inputInstanceId + '_div').css("display", "none");
		$.each( inputData.outputs, function( outputIndex, outputData ) {
			$('#inputInstance' + inputInstanceId + '_output' + outputIndex + '_div').html();
		});
	});

}


function showPatternDetails(moduleId, patternInstanceId){
	hideAllInputs();
	currentView.activeSections[moduleId] = patternInstanceId
	$('#inputs').detach().appendTo('#' + moduleId + '_pattern' + patternInstanceId);
	$.each(allSculptureData.currentSculpture.modules[moduleId].patterns[patternInstanceId].inputs, function(patternInputId, patternInputData){
		idPrefix  = 'inputInstance' + patternInputData.inputInstanceId + '_';
		$('#' + idPrefix + 'div').css("display", "block");
		$('#' + idPrefix + 'description').html(patternInputData.description);
		$.each(allSculptureData.inputs[patternInputData.inputInstanceId].outputs, function(outputIndex, outputData){
			if (outputIndex == patternInputData.outputIndexOfInput || patternInputData.type=='multi'){
				html = '<span class="inputDescription">Current type:<br>' + allSculptureData.inputs[patternInputData.inputInstanceId].shortDescription + ' ' + outputData.description + '</span>';
				html += '<button id="' + moduleId + '_' + patternInstanceId + '_' + patternInputId + '_rebindButton" class="rebindButton">Change</button>';
				$('#inputInstance' + patternInputData.inputInstanceId + '_outputs').html(html);
			}
		});
	});
	$('.rebindButton').button().click(function(e){
		var parts = this.id.split('_');
		showRebindDialog(parts[0], parts[1], parts[2]);
	});

}
function changeSculpture(){
	if ($('#sculptureChooser').val() != 'none'){
		doCommand(['loadSculpture', $('#sculptureChooser').val()]);
	}
}
function doCommand(command){
	commandStr = JSON.stringify(command)
	$('#logDiv').prepend('Command sent:' + commandStr + '<br>');
	$.ajax(settings.serverUrl + 'doCommand', {
		data : commandStr,
		contentType : 'application/json',
		type : 'POST',
		dataType: 'json',
	}).done(function(result) {
		handleCommandResult(result);
	});
}
function handleCommandResult(result){
	resultStr = JSON.stringify(result)

	//$('#logDiv').prepend('Result recieved:' + resultStr + '<br>');
	if ($.inArray(result.command, ['removePattern', 'loadSculpture', 'addPattern', 'changePatternInputBinding', 'bindPatternToNewInput', 'addGlobalInput', 'removeGlobalInput']) > -1){
		if (allSculptureData.currentSculpture){
			currentView.sculptureIsLoaded = true;
		}
		reloadData();
	}

}
function addPattern(moduleId){
	inputId = '#' + moduleId + '_patternChoices';
	if ($(inputId).val() != 'none'){
		doCommand(['addPattern', moduleId, $(inputId).val()]);
		$(inputId).val('none');
	}
}
function setInputValue(inputInstanceId, settingIndex){
	htmlId = '#inputInstance' + inputInstanceId + '_input' + settingIndex;
	doCommand(['setInputValue', parseInt(inputInstanceId), $(htmlId).val(), parseInt(settingIndex)]);
}
function setInputToggle(inputInstanceId, settingIndex){
	htmlId = '#inputInstance' + inputInstanceId + '_input' + settingIndex;
	doCommand(['setInputValue', parseInt(inputInstanceId), $(htmlId).is(":checked"), parseInt(settingIndex)]);
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
