var test = function(e){
	alert ('tested');

};

$(document).ready(function(e){
		$("#status_codes").click(function(e){
			$('#content').load("http://localhost:5000/sc/")	;			
		});
		$("#hosts_list").click(function(e){
			$('#content').load("http://localhost:5000/hl/")	;			
		});
		$("#event_list").click(function(e){
			$('#content').load("http://localhost:5000/el/")	;		

		});
		$("#config_display").click(function(e){
			$('#content').load("http://localhost:5000/cfg/")	;		

		});
		$("#active_checks").click(function(e){
			$('#content').load("http://localhost:5000/listChecks/CHECK_RUNNING");

		});

		$("#queued_checks").click(function(e){
			$('#content').load("http://localhost:5000/listChecks/CHECK_SCHEDULED");
			
		});
		$("#failed_checks").click(function(e){
			$('#content').load("http://localhost:5000/listChecks/CHECK_FAILED");
			
		});
		$("#rerun_checks").click(function(e){
			$('#content').load("http://localhost:5000/listChecks/CHECK_RERUN");
			
		});
		$("#comleted_checks").click(function(e){
			$('#content').load("http://localhost:5000/listChecks/CHECK_SUCCESSFULL");
			
		});
		$("#x").click(function(e){
			$('#myModal').modal('show');
			
		});
		
});

