type LogoProps = {
  className?: string;
};

const Logo = ({ className }: LogoProps): React.JSX.Element => (
  <span className={`${className} font-logo text-3xl select-none`}>YorkX</span>
);

export default Logo;
