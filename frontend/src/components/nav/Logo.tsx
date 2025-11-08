type LogoProps = {
  className?: string;
};

const Logo = ({ className }: LogoProps): React.JSX.Element => (
  <span className={`${className} font-logo text-md tracking-wider select-none`}>
    STOCK EXCHANGE TERMINAL
  </span>
);

export default Logo;
