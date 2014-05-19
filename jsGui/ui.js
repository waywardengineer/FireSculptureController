var settings = {
	'serverUrl' : '/'
};
var allSculptureData = false;
var activeTab = false;
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

function showRebindDialog(patternInstanceId, patternInputId){
	$('#dialog').dialog('open');

}

function doInit(){
	$('#dialog').dialog({
			autoOpen: false,
			height: 300,
			width: 350,
			modal: true,
			buttons: {
				"Update": function() {
					$(this).dialog("close");
				},
				"Cancel": function() {
					$(this).dialog("close");
				}
			}
	});
	reloadData();
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
	$('#mainDiv').html('');
	if (allSculptureData.currentSculpture){
		$('#mainDiv').append($('#sculptureControllerTemplate').render(makeSculptureControllerTemplateData()));
		$.each( allSculptureData.inputs, function( inputInstanceId, inputData ) {
			buildInputControls(inputInstanceId, inputData);
		});
		$.each( allSculptureData.currentSculpture.modules, function( moduleId, moduleData ) {
			$('#' + moduleId + '_patternChoices').menu();
			$('#' + moduleId + '_patternSelection').menu();
		});
		$('.pooferDisplay').button();
		if (activeTab){
			$('#sculptureControl').tabs({ active : $("#sculptureControl>div").index($("#" + activeTab)) });
		}
		else{
			$('#sculptureControl').tabs();
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
			inputId = 'inputInstance' + inputInstanceId + '_setting' + settingIndex;
			templateData = settingData;
			templateData['id'] = inputId;
			templateData['inputInstanceId'] = inputInstanceId;
			templateData['settingIndex'] = settingIndex;
			
			switch(settingData['type']){
				case 'pulse':
					if (settingData.currentValue){
						templateData['checked'] = 'checked="checked"';
					}
					else {
						templateData['checked'] = '';
					}
					templateData['controlHtml'] =  $('#buttonTemplate').render(templateData);
					$(htmlParentId).append($('#inputControlTemplate').render(templateData));
					$('#' + inputId).button().click(function(e){
						setInputToggle(inputInstanceId, settingIndex);
					});
				break;
				case 'value':
					templateData['controlHtml'] =  $('#knobTemplate').render(templateData);
					$(htmlParentId).append($('#inputControlTemplate').render(templateData));
					initKnob(inputId, inputInstanceId, settingIndex);
				break;
			}
			$(htmlParentId).append('<span class="settingLabel">' + settingData.description + '</span>');
		});
		$.each( inputData.outputs, function( outputIndex, outputData ) {
			$(htmlParentId).append('<div id="inputInstance' + inputInstanceId + '_output' + outputIndex + '_reBindDiv"></div>');
		});
	}
}
function editPattern(moduleId){
	patternInstanceId = $('#' + moduleId + '_patternSelection').val();
	$.each(allSculptureData.inputs, function(inputInstanceId, inputData){
		$('#inputInstance' + inputInstanceId + '_div').css("display", "none");
		$.each( inputData.outputs, function( outputIndex, outputData ) {
			$('#inputInstance' + inputInstanceId + '_output' + outputIndex + '_reBindDiv').html();
		});
	});
	$.each(allSculptureData.currentSculpture.modules[moduleId].patterns[patternInstanceId].inputBindings, function(patternInputId, patternInputData){
		idPrefix  = 'inputInstance' + patternInputData.inputInstanceId + '_';
		$('#' + idPrefix + 'div').css("display", "block");
		$('#' + idPrefix + 'description').html(patternInputData.description);
		$.each(allSculptureData.inputs[patternInputData.inputInstanceId].outputs, function(outputIndex, outputData){
			idPrefix = 'inputInstance' + patternInputData.inputInstanceId + '_output' + outputIndex + '_reBind'
			html = '<button id="' + idPrefix + 'Button">' + allSculptureData.inputs[patternInputData.inputInstanceId].description + '</button>'
			$('#' + idPrefix + 'Div').html(html);
			$('#' + idPrefix + 'Button').button().click(function(e){
				showRebindDialog(patternInstanceId, patternInputId);
			});
		});
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
			reloadData();
		case 'addPattern':
			reloadData();
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
function setInputValue(inputInstanceId, settingIndex){
	htmlId = '#inputInstance' + inputInstanceId + '_setting' + settingIndex;
	doCommand(['setInputValue', parseInt(inputInstanceId), $(htmlId).val(), parseInt(settingIndex)]);
}
function setInputToggle(inputInstanceId, settingIndex){
	htmlId = '#inputInstance' + inputInstanceId + '_setting' + settingIndex;
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
