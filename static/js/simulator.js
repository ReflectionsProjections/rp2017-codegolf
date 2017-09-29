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
});
