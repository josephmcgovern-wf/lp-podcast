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
            sleep(time: 5, unit: 'HOURS')
            echo 'I am all done'
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