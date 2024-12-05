import React from 'react';
import ReactDOM from 'react-dom';
import Header from './components/Header';
import TaskList from './components/TaskList';
import PageFooter from './components/PageFooter';

function TaskManagerApp() {
    return (
        <div className="task-manager-container">
            <Header />
            <TaskList />
            <PageFooter />
        </div>
    );
}

ReactDOM.render(<TaskManagerApp />, document.getElementById('root'));