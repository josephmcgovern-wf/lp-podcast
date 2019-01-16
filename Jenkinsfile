pipeline {
  agent any
  stages {
    stage('Pre-deploy') {
      parallel {
        stage('Basic commands') {
          steps {
            sh '''echo "hello, world!"
ls'''
            sleep 5
            sh 'echo "I am done sleeping!"'
          }
        }
        stage('Parallel commands') {
          steps {
            echo 'hello'
            echo 'I am all done'
            waitUntil() {
              sleep 10
              input 'Feel free to override'
            }

          }
        }
      }
    }
    stage('Wrap-up') {
      steps {
        echo 'Everything is complete!'
      }
    }
  }
}