// Set custom text area properties
var textbox = document.getElementById('repl');
textbox.onkeydown = function(e){
    if(e.keyCode==9 || e.which==9){
        e.preventDefault();
        var s = this.selectionStart;
        this.value = this.value.substring(0,this.selectionStart) + '\t' + this.value.substring(this.selectionEnd);
        this.selectionEnd = s+1;
    }
}


// AngularJS controller
var app = angular.module('codeGolfApp', []);
app.controller('codeGolfCtrl', function($scope, $http) {
    if(username=='null'){
        $scope.username = null;
    } else {
        $scope.username = username;
    }
    $scope.task_id = task_id;
    $scope.leaderboard = leaderboard;
    if(!task_id){
        $http({
            method: 'GET',
            url: '/golf/task_list'
        }).then(function callbackSuccess(response){
            $scope.tasks = response.data;
            console.log($scope.tasks);
        }, function callbackFailure(response){
            console.log('request failed');
        });
    }
    $scope.setBoilerplate = function(){
        language = document.getElementById('language').value;
        switch(language) {
            case 'cc':
                document.getElementById('repl').value='#include <stdlib.h>\n#include <stdio.h>\nint main(int argc, char *argv[]){\n\tint i=atoi(argv[1]);\n\tprintf("%d",i);\n\treturn 0;\n}';
                break;
            case 'java':
                document.getElementById('repl').value='public class Answer{\n\tpublic static void main(String[] args){\n\t\tint i=Integer.parseInt(args[0]);\n\t\tSystem.out.println(i);\n\t}\n}';
                break;
            case 'js':
                document.getElementById('repl').value='i=parseInt(process.argv[2])\nconsole.log(i)';
                break;
            case 'py':
                document.getElementById('repl').value='import sys\n\ti=int(sys.argv[1])\n\tprint(i)';
                break;
        } 
    };
    console.log($scope.setBoilerplate);
});
