// ErrorBoundary.js
import React, { Component } from 'react';

class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        // Update state so next render will show fallback UI.
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // You can log error to an error reporting service here
        console.error("Uncaught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            // You can render any custom fallback UI
            return <h2>Something went wrong.</h2>;
        }
        return this.props.children; 
    }
}
export default ErrorBoundary;
```
```jsx
import React from 'react';
import ReactDOM from 'react-dom';
import Header from './components/Header';
import TaskList from './components/TaskList';
import PageFooter from './components/PageFooter';
import ErrorBoundary from './ErrorBoundary'; // Import ErrorBoundary component

function TaskManagerApp() {
    return (
        <div className="task-manager-container">
            <ErrorBoundary>
                <Header />
            </ErrorBoundary>
            <ErrorBoundary>
                <TaskList />
            </ErrorBoundary>
            <ErrorBoundary>
                <PageFooter />
            </ErrorBoundary>
        </div>
    );
}

ReactDOM.render(<TaskManagerApp />, document.getElementById('root'));