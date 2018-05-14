pipeline {
    agent {
        label 'node-cloudlab002'
    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
    }
    triggers {
        pollSCM('H/2 * * * *')
    }
    stages {
        stage('pre.git') {
            steps {
                sh '''
                    root="/apps/data/tomcat_8080/jenkins_file"
                    python_folder=$root/python/forward
                    source ~/.bash_profile>/dev/null 2>&1
                    pyenv activate forward
                    pip install -r requirements.txt >/dev/null
                    python setup.py clean --all >/dev/null
                '''
            }
        }
        stage('pre.unittest+flake8') {
            steps {
                sh '''
                    #flake8_check
                    source ~/.bash_profile>/dev/null 2>&1
                    pyenv activate forward
                    echo ">[run flake8]"
                    flake8 ./ --config=protocol/flake8
                    result_flake8=$?
                    echo ">[run nosetest]"
                    nosetests -c nosetests.ini
                    result_nosetests=$?
                    if [ ! $result_flake8 -eq 0 ] || [ ! $result_nosetests -eq 0 ];then
                        echo "[ERROR]: test pre failed!"
                        exit 1
                    fi
                    #cp $WORKSPACE/unittests/nosetests.xml
                    #cp $WORKSPACE/unittests/coverage.xml
                '''
                cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'unittests/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
                junit 'unittests/nosetests.xml'
            }
        }
        stage('pre.install') {
            steps {
                sh '''
                    #setuptools
                    source ~/.bash_profile>/dev/null 2>&1
                    pyenv activate forward
                    echo ">[build & install]"
                    python setup.py install
                '''
            }
        }
        stage('pre.regression') {
            steps {
                sh '''
                    source ~/.bash_profile>/dev/null 2>&1
                    pyenv activate forward
                    echo ">[run regression testing]"
                    echo "Null, Waiting for add..."
                '''
            }
        }
    }
    post {
        success {
            emailext body: '''
                <p>Forward开源版-预发布环境-CI</p>
                <br>
                <p>Forward develop分支提交构建已完成</p>
            ''',
            postsendScript: '$DEFAULT_POSTSEND_SCRIPT',
            presendScript: '$DEFAULT_PRESEND_SCRIPT',
            subject: '[Success][预发布-Forward开源版] $DEFAULT_SUBJECT',
            to: '13802880354@139.com,zhangqc@fits.com.cn'
        }
        failure {
            emailext(subject: '[Failed][预发布-Forward开源版]$DEFAULT_SUBJECT', body: '$DEFAULT_CONTENT', to: '13802880354@139.com,zhangqc@fits.com.cn')
        }
    }
}
