import React from 'react';
import { Link } from 'react-router-dom';
import styles from './header.module.css';

export interface HeaderProps {
  /**
   * The current active route
   */
  activeRoute?: string;
}

/**
 * Application header with navigation using modular CSS
 */
export const Header: React.FC<HeaderProps> = ({ activeRoute = '/' }) => {
  // Consider both '/' and '/create' as the create route since they show the same component
  const isCreateRoute = activeRoute === '/' || activeRoute === '/create';
  
  return (
    <header className={styles.headerContainer}>
      <div className={styles.innerContainer}>
        <div className={styles.headerRow}>
          {/* Logo and title */}
          <div className={styles.logoWrapper}>
            <Link to="/" className={styles.logoLink}>
              <div className={styles.logoCircle}>
                CV
              </div>
              <h1 className={styles.titleText}>
                Concept Visualizer
              </h1>
            </Link>
          </div>
          
          {/* Navigation */}
          <nav className={styles.navContainer}>
            <Link 
              to="/create" 
              className={isCreateRoute ? styles.activeNavLink : styles.inactiveNavLink}
            >
              <span className={styles.navIcon}>✨</span>Create
            </Link>
            
            <Link 
              to="/concepts/refine" 
              className={activeRoute.includes('/concepts/refine') ? styles.activeNavLink : styles.inactiveNavLink}
            >
              <span className={styles.navIcon}>🔄</span>Refine
            </Link>
            
            <Link 
              to="/recent" 
              className={activeRoute === '/recent' ? styles.activeNavLink : styles.inactiveNavLink}
            >
              <span className={styles.navIcon}>📚</span>Recent
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}; 